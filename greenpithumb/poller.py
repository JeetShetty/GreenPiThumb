import datetime
import logging
import threading

import pytz

import db_store

logger = logging.getLogger(__name__)

_SECONDS_PER_MINUTE = 60
# Number of seconds to idle between checks for whether a poller needs to poll or
# a poller needs to stop (note that this is NOT the total time a poller sleeps
# between polls).
_IDLE_SECONDS = 0.5


class SensorPollerFactory(object):
    """Factory for creating sensor poller objects."""

    def __init__(self, make_scheduler_func, record_queue):
        """Create a new SensorPollerFactory instance.

        Args:
            make_scheduler_func: A function for creating a polling scheduler.
            record_queue: Queue on which to place database records.
        """
        self._make_scheduler_func = make_scheduler_func
        self._record_queue = record_queue

    def create_temperature_poller(self, temperature_sensor):
        return _SensorPoller(
            _TemperaturePollWorker(self._make_scheduler_func(),
                                   self._record_queue, temperature_sensor))

    def create_humidity_poller(self, humidity_sensor):
        return _SensorPoller(
            _HumidityPollWorker(self._make_scheduler_func(), self._record_queue,
                                humidity_sensor))

    def create_light_poller(self, light_sensor):
        return _SensorPoller(
            _LightPollWorker(self._make_scheduler_func(), self._record_queue,
                             light_sensor))

    def create_soil_watering_poller(self, soil_moisture_sensor, pump_manager):
        return _SensorPoller(
            _SoilWateringPollWorker(self._make_scheduler_func(
            ), self._record_queue, soil_moisture_sensor, pump_manager))

    def create_camera_poller(self, camera_manager):
        return _SensorPoller(
            _CameraPollWorker(self._make_scheduler_func(), self._record_queue,
                              camera_manager))


def _datetime_to_unix_time(dt):
    """Converts a datetime into seconds since UNIX epoch."""
    unix_epoch = datetime.datetime(year=1970, month=1, day=1, tzinfo=pytz.utc)
    return int((dt - unix_epoch).total_seconds())


def _unix_time_to_datetime(unix_time):
    """Converts a UNIX timestamp to a UTC datetime."""
    return datetime.datetime.fromtimestamp(unix_time, tz=pytz.utc)


def _round_up_to_multiple(value, multiple):
    """Rounds an integer value up to a multiple specified."""
    mod = value % multiple
    # Value is already an exact multiple, so return the original value.
    if mod == 0:
        return value
    # Round up to next multiple
    return (value - mod) + multiple


class Scheduler(object):
    """Scheduler for choosing the next time a poller performs a poll."""

    def __init__(self, clock, poll_interval):
        """Creates a new Scheduler instance.

        Args:
            clock: A clock interface.
            poll_interval: A timedelta representing how often the data should be
                polled.
        """
        self._clock = clock
        self._poll_interval = poll_interval
        self._last_poll_time = None

    def _unix_now(self):
        return _datetime_to_unix_time(self._clock.now())

    def _next_poll_time_unix(self):
        """Calculates time of next poll in UNIX time.

        Calculates time of next poll so that it is a multiple of
        self._poll_interval. If the next multiple is the same as the last poll
        time, returns a poll time that is the current time + one poll interval.

        Returns:
            UNIX time of next scheduled poll.
        """
        next_poll_time_unix = _round_up_to_multiple(
            self._unix_now(), int(self._poll_interval.total_seconds()))
        if self._last_poll_time and (
                next_poll_time_unix == _datetime_to_unix_time(
                    self._last_poll_time)):
            next_poll_time_unix += int(self._poll_interval.total_seconds())

        return next_poll_time_unix

    def wait_until_poll_time(self, timeout):
        """Waits until the next poll time.

        Args:
            timeout: The maximum time (in seconds) to wait for the next poll
                time.

        Returns:
            True if wait to poll time completed, False if wait timed out.
        """
        next_poll_time_unix = self._next_poll_time_unix()
        seconds_until_poll_time = next_poll_time_unix - self._unix_now()
        wait_seconds = min(seconds_until_poll_time, timeout)
        if wait_seconds:
            self._clock.wait(wait_seconds)
        # If we didn't time out waiting, return True and update the last poll
        # time.
        if seconds_until_poll_time <= timeout:
            self._last_poll_time = _unix_time_to_datetime(next_poll_time_unix)
            return True
        return False

    def last_poll_time(self):
        return self._last_poll_time


class _SensorPollWorkerBase(object):
    """Base class for sensor poll worker.

    The poll worker is the class that handles all the work and context for the
    background polling thread.
    """

    def __init__(self, scheduler, record_queue, sensor):
        """Create a new _SensorPollWorkerBase instance

        Args:
            scheduler: Poll time scheduler.
            record_queue: Queue on which to place database records.
            sensor: A sensor to poll for status. The particular type of sensor
                will vary depending on the poll worker subclass.
        """
        self._scheduler = scheduler
        self._record_queue = record_queue
        self._sensor = sensor
        self._stopped = threading.Event()

    def _is_stopped(self):
        return self._stopped.is_set()

    def _wait_until_poll_time_or_stop(self):
        while not self._is_stopped():
            if self._scheduler.wait_until_poll_time(_IDLE_SECONDS):
                return

    def poll(self):
        """Polls at a fixed interval until caller calls stop()."""
        logger.info('polling starting for %s', self.__class__.__name__)
        while True:
            self._wait_until_poll_time_or_stop()
            if self._is_stopped():
                break
            self._poll_once()
        logger.info('polling terminating for %s', self.__class__.__name__)

    def stop(self):
        """End worker polling."""
        self._stopped.set()


class _TemperaturePollWorker(_SensorPollWorkerBase):
    """Polls a temperature sensor and stores the readings."""

    def _poll_once(self):
        """Polls for current temperature and queues DB record."""
        temperature = self._sensor.temperature()
        self._record_queue.put(
            db_store.TemperatureRecord(self._scheduler.last_poll_time(),
                                       temperature))


class _HumidityPollWorker(_SensorPollWorkerBase):
    """Polls a humidity sensor and stores the readings."""

    def _poll_once(self):
        """Polls for and stores current relative humidity."""
        humidity = self._sensor.humidity()
        self._record_queue.put(
            db_store.HumidityRecord(self._scheduler.last_poll_time(), humidity))


class _LightPollWorker(_SensorPollWorkerBase):
    """Polls a light sensor and stores the readings."""

    def _poll_once(self):
        light = self._sensor.light()
        self._record_queue.put(
            db_store.LightRecord(self._scheduler.last_poll_time(), light))


class _SoilWateringPollWorker(_SensorPollWorkerBase):
    """Polls for and records watering event data.

    Polls soil moisture sensor and oversees a water pump based to add water when
    the moisture drops too low. Records both soil moisture and watering events.
    """

    def __init__(self, scheduler, record_queue, soil_moisture_sensor,
                 pump_manager):
        """Creates a new SoilWateringPoller object.

        Args:
            scheduler: Poll time scheduler.
            record_queue: Queue on which to place soil moisture records and
                watering event records for storage.
            soil_moisture_sensor: An interface for reading the soil moisture
                level.
            pump_manager: An interface to manage a water pump.
        """
        super(_SoilWateringPollWorker, self).__init__(scheduler, record_queue,
                                                      soil_moisture_sensor)
        self._pump_manager = pump_manager

    def _poll_once(self):
        """Polls soil moisture and adds water if moisture is too low.

        Checks soil moisture levels and records the current level. Using the
        current soil moisture level, checks if the pump needs to run, and if so,
        runs the pump and records the watering event.
        """
        soil_moisture = self._sensor.soil_moisture()
        self._record_queue.put(
            db_store.SoilMoistureRecord(self._scheduler.last_poll_time(),
                                        soil_moisture))
        ml_pumped = self._pump_manager.pump_if_needed(soil_moisture)
        if ml_pumped > 0:
            self._record_queue.put(
                db_store.WateringEventRecord(self._scheduler.last_poll_time(),
                                             ml_pumped))


class _CameraPollWorker(_SensorPollWorkerBase):
    """Captures and stores pictures pictures from a camera."""

    def _poll_once(self):
        """Captures and stores an image."""
        if self._sensor.sufficient_light():
            self._sensor.save_photo()

    def stop(self):
        """End worker polling and close camera."""
        self._sensor.close()
        super(_CameraPollWorker, self).stop()


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
