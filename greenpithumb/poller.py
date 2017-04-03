import datetime
import logging
import threading

import pytz

import db_store

logger = logging.getLogger(__name__)

# Number of seconds to idle between checks for whether a poller needs to poll or
# a poller needs to stop (note that this is NOT the total time a poller sleeps
# between polls).
_IDLE_SECONDS = 0.5


class SensorPollerFactory(object):
    """Factory for creating sensor poller objects."""

    def __init__(self, clock, poll_interval, record_queue):
        """Create a new SensorPollerFactory instance.

        Args:
            clock: A clock interface.
            poll_interval: An int of how often the data should be polled for,
                in seconds.
            record_queue: Queue on which to place database records.
        """
        self._clock = clock
        self._poll_interval = poll_interval
        self._record_queue = record_queue

    def create_temperature_poller(self, temperature_sensor):
        return _SensorPoller(
            _TemperaturePollWorker(self._clock, self._poll_interval,
                                   self._record_queue, temperature_sensor))

    def create_humidity_poller(self, humidity_sensor):
        return _SensorPoller(
            _HumidityPollWorker(self._clock, self._poll_interval,
                                self._record_queue, humidity_sensor))

    def create_ambient_light_poller(self, light_sensor):
        return _SensorPoller(
            _AmbientLightPollWorker(self._clock, self._poll_interval,
                                    self._record_queue, light_sensor))

    def create_soil_watering_poller(self, moisture_sensor, pump_manager):
        return _SensorPoller(
            _SoilWateringPollWorker(self._clock, self._poll_interval,
                                    self._record_queue, moisture_sensor,
                                    pump_manager))

    def create_camera_poller(self, camera_manager):
        return _SensorPoller(
            _CameraPollWorker(self._clock, self._poll_interval,
                              self._record_queue, camera_manager))


def _datetime_to_unix_time(dt):
    """Converts a datetime into seconds since UNIX epoch."""
    unix_epoch = datetime.datetime(year=1970, month=1, day=1, tzinfo=pytz.utc)
    return int((dt - unix_epoch).total_seconds())


def _round_up_to_multiple(value, multiple):
    """Rounds an integer value up to a multiple specified."""
    mod = value % multiple
    # Value is already an exact multiple, so return the original value.
    if mod == 0:
        return value
    # Round up to next multiple
    return (value - mod) + multiple


class _SensorPollWorkerBase(object):
    """Base class for sensor poll worker.

    The poll worker is the class that handles all the work and context for the
    background polling thread.
    """

    def __init__(self, clock, poll_interval, record_queue, sensor):
        """Create a new _SensorPollWorkerBase instance

        Args:
            clock: A clock interface.
            poll_interval: An int of how often the data should be polled for,
                in seconds.
            record_queue: Queue on which to place database records.
            sensor: A sensor to poll for status. The particular type of sensor
                will vary depending on the poll worker subclass.
        """
        self._clock = clock
        self._poll_interval = poll_interval
        self._record_queue = record_queue
        self._sensor = sensor
        self._stopped = threading.Event()

    def _unix_now(self):
        return _datetime_to_unix_time(self._clock.now())

    def _wait_until_unix_time(self, target_unix_time):
        """Waits until the target time arrives or the worker is stopped.

        Args:
            target_unix_time: UNIX time to wait until.
        """
        logger.info('%s is waiting %d seconds until next poll',
                    self.__class__.__name__,
                    target_unix_time - self._unix_now())
        while not self._is_stopped() and (self._unix_now() < target_unix_time):
            self._clock.wait(_IDLE_SECONDS)

    def _next_poll_time(self, last_poll_time):
        """Calculates time of next poll in UNIX time.

        Calculates time of next poll so that it is a multiple of
        self._poll_interval. If the next multiple is the same as the last poll
        time, returns a poll time that is the current time + one poll interval.

        Args:
            last_poll_time: The UNIX time of the last poll or None if this is
                the first poll.

        Returns:
            UNIX time of next scheduled poll.
        """
        next_poll_time = _round_up_to_multiple(self._unix_now(),
                                               self._poll_interval)
        if last_poll_time and (next_poll_time == last_poll_time):
            next_poll_time += self._poll_interval
        return next_poll_time

    def _is_stopped(self):
        return self._stopped.is_set()

    def poll(self):
        """Polls at a fixed interval until caller calls stop()."""
        logger.info('polling starting for %s', self.__class__.__name__)
        next_poll_time = self._next_poll_time(last_poll_time=None)
        while True:
            self._wait_until_unix_time(next_poll_time)
            if self._is_stopped():
                break
            self._poll_once()
            next_poll_time = self._next_poll_time(last_poll_time=next_poll_time)
        logger.info('polling terminating for %s', self.__class__.__name__)

    def stop(self):
        """End worker polling."""
        self._stopped.set()


class _TemperaturePollWorker(_SensorPollWorkerBase):
    """Polls a temperature sensor and stores the readings."""

    def _poll_once(self):
        """Polls for current ambient temperature and queues DB record."""
        temperature = self._sensor.temperature()
        self._record_queue.put(
            db_store.TemperatureRecord(self._clock.now(), temperature))


class _HumidityPollWorker(_SensorPollWorkerBase):
    """Polls a humidity sensor and stores the readings."""

    def _poll_once(self):
        """Polls for and stores current relative humidity."""
        humidity = self._sensor.humidity()
        self._record_queue.put(
            db_store.HumidityRecord(self._clock.now(), humidity))


class _AmbientLightPollWorker(_SensorPollWorkerBase):
    """Polls an ambient light sensor and stores the readings."""

    def _poll_once(self):
        ambient_light = self._sensor.ambient_light()
        self._record_queue.put(
            db_store.AmbientLightRecord(self._clock.now(), ambient_light))


class _SoilWateringPollWorker(_SensorPollWorkerBase):
    """Polls for and records watering event data.

    Polls soil moisture sensor and oversees a water pump based to add water when
    the moisture drops too low. Records both soil moisture and watering events.
    """

    def __init__(self, clock, poll_interval, record_queue, soil_moisture_sensor,
                 pump_manager):
        """Creates a new SoilWateringPoller object.

        Args:
            clock: A clock interface.
            poll_interval: An int of how often the data should be polled for,
                in seconds.
            record_queue: Queue on which to place soil moisture records and
                watering event records for storage.
            soil_moisture_sensor: An interface for reading the soil moisture
                level.
            pump_manager: An interface to manage a water pump.
        """
        super(_SoilWateringPollWorker, self).__init__(
            clock, poll_interval, record_queue, soil_moisture_sensor)
        self._pump_manager = pump_manager

    def _poll_once(self):
        """Polls soil moisture and adds water if moisture is too low.

        Checks soil moisture levels and records the current level. Using the
        current soil moisture level, checks if the pump needs to run, and if so,
        runs the pump and records the watering event.
        """
        soil_moisture = self._sensor.moisture()
        self._record_queue.put(
            db_store.SoilMoistureRecord(self._clock.now(), soil_moisture))
        ml_pumped = self._pump_manager.pump_if_needed(soil_moisture)
        if ml_pumped > 0:
            self._record_queue.put(
                db_store.WateringEventRecord(self._clock.now(), ml_pumped))


class _CameraPollWorker(_SensorPollWorkerBase):
    """Captures and stores pictures pictures from a camera."""

    def _poll_once(self):
        """Captures and stores an image."""
        self._sensor.save_photo()


class _SensorPoller(object):
    """Spawns and manages poll workers in background threads."""

    def __init__(self, poll_worker):
        """Creates a new _SensorPoller object for polling sensors.

        Args:
            poll_worker: Worker object that handles the polling work.
        """
        self._worker = poll_worker

    def start_polling_async(self):
        """Starts a new thread to begin polling."""
        t = threading.Thread(target=self._worker.poll)
        t.setDaemon(True)
        t.start()

    def close(self):
        """Stops polling."""
        self._worker.stop()
