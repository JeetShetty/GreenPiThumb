import threading

import db_store


class SensorPollerBase(object):
    """Base class for sensor polling."""

    def __init__(self, local_clock, poll_interval):
        """Creates a new SensorPollerBase object for polling sensors.

        Args:
            local_clock: A local time zone clock interface.
            poll_interval: An int of how often the sensor should be polled, in
                seconds.
        """
        self._local_clock = local_clock
        self._poll_interval = poll_interval
        self._closed = threading.Event()

    def _poll(self):
        """Polls at a fixed interval until caller calls close()."""
        while not self._closed.is_set():
            self._poll_once()
            self._local_clock.wait(self._poll_interval)

    def start_polling_async(self):
        """Starts a new thread to begin polling."""
        t = threading.Thread(target=self._poll)
        t.setDaemon(True)
        t.start()

    def close(self):
        """Stops polling."""
        self._closed.set()


class TemperaturePoller(SensorPollerBase):
    """Polls a temperature sensor and stores the readings."""

    def __init__(self, local_clock, poll_interval, temperature_sensor,
                 record_queue):
        """Creates a new TemperaturePoller object.

        Args:
            local_clock: A local time zone clock interface.
            poll_interval: An int of how often the sensor should be polled, in
                seconds.
            temperature_sensor: An interface for reading the temperature.
            record_queue: Queue on which to place temperature records for
              storage.
        """
        super(TemperaturePoller, self).__init__(local_clock, poll_interval)
        self._temperature_sensor = temperature_sensor
        self._record_queue = record_queue

    def _poll_once(self):
        """Polls for current ambient temperature and queues DB record."""
        temperature = self._temperature_sensor.temperature()
        self._record_queue.put(
            db_store.TemperatureRecord(self._local_clock.now(), temperature))


class HumidityPoller(SensorPollerBase):
    """Polls a humidity sensor and stores the readings."""

    def __init__(self, local_clock, poll_interval, humidity_sensor,
                 record_queue):
        """Creates a new HumidityPoller object.

        Args:
            local_clock: A local time zone clock interface.
            poll_interval: An int of how often the sensor should be polled, in
                seconds.
            humidity_sensor: An interface for reading the humidity.
            record_queue: Queue on which to place humidity records for storage.
        """
        super(HumidityPoller, self).__init__(local_clock, poll_interval)
        self._humidity_sensor = humidity_sensor
        self._record_queue = record_queue

    def _poll_once(self):
        """Polls for and stores current relative humidity."""
        humidity = self._humidity_sensor.humidity()
        self._record_queue.put(
            db_store.HumidityRecord(self._local_clock.now(), humidity))


class MoisturePoller(SensorPollerBase):
    """Polls a soil moisture sensor and stores the readings."""

    def __init__(self, local_clock, poll_interval, moisture_sensor,
                 record_queue):
        """Creates a MoisturePoller object.

        Args:
            local_clock: A local time zone clock interface.
            poll_interval: An int of how often the sensor should be polled, in
                seconds.
            moisture_sensor: An interface for reading the soil moisture level.
            record_queue: Queue on which to place moisture records for storage.
        """
        super(MoisturePoller, self).__init__(local_clock, poll_interval)
        self._moisture_sensor = moisture_sensor
        self._record_queue = record_queue

    def _poll_once(self):
        """Polls current soil moisture."""
        soil_moisture = self._moisture_sensor.moisture()
        self._record_queue.put(
            db_store.SoilMoistureRecord(self._local_clock.now(), soil_moisture))


class AmbientLightPoller(SensorPollerBase):
    """Polls an ambient light sensor and stores the readings."""

    def __init__(self, local_clock, poll_interval, light_sensor, record_queue):
        """Creates a new AmbientLightPoller object.

        Args:
            local_clock: A local time zone clock interface.
            poll_interval: An int of how often the sensor should be polled, in
                seconds.
            light_sensor: An interface for reading the ambient light level.
            record_queue: Queue on which to place ambient light records for
              storage.
        """
        super(AmbientLightPoller, self).__init__(local_clock, poll_interval)
        self._light_sensor = light_sensor
        self._record_queue = record_queue

    def _poll_once(self):
        ambient_light = self._light_sensor.ambient_light()
        self._record_queue.put(
            db_store.AmbientLightRecord(self._local_clock.now(), ambient_light))


# TODO(mtlynch): Fix this so that it can access soil moisture data in a
# thread-safe way. Currently it won't be able to access the soil moisture store
# because the thread that calls it is different from the thread that created
# the store's DB connection.
class WateringEventPoller(SensorPollerBase):
    """Polls for and records watering event data.

    Polls for latest soil moisture readings and oversees a water pump based on
    those readings.
    """

    def __init__(self, local_clock, poll_interval, pump_manager,
                 soil_moisture_store, record_queue):
        """Creates a new WateringEventPoller object.

        Args:
            local_clock: A local time zone clock interface.
            poll_interval: An int of how often the data should be polled for,
                in seconds.
            pump_manager: An interface to manage a water pump.
            soil_moisture_store: An interface for retrieving soil moisture
                readings.
            record_queue: Queue on which to place watering event records for
              storage.
        """
        super(WateringEventPoller, self).__init__(local_clock, poll_interval)
        self._pump_manager = pump_manager
        self._soil_moisture_store = soil_moisture_store
        self.record_queue = record_queue

    def _poll_once(self):
        """Oversees a water pump, and polls for and stores watering event data.

        Polls for latest soil moisture readings and feeds them to a water pump.
        If the pump runs, it stores the event data.
        """
        soil_moisture = self._soil_moisture_store.latest_soil_moisture()
        if soil_moisture:
            ml_pumped = self._pump_manager.pump_if_needed(soil_moisture)
            if ml_pumped > 0:
                self.record_queue.put(
                    db_store.WateringEventRecord(self._local_clock.now(),
                                                 ml_pumped))


class CameraPoller(SensorPollerBase):
    """Captures and stores pictures pictures from a camera."""

    def __init__(self, local_clock, poll_interval, camera_manager):
        """Creates a new CameraPoller object.

        Args:
            local_clock: A local time zone clock interface.
            poll_interval: An int of how often the images should be captured,
                in seconds.
            camera_manager: An interface for capturing images.
        """
        super(CameraPoller, self).__init__(local_clock, poll_interval)
        self._camera_manager = camera_manager

    def _poll_once(self):
        """Captures and stores an image."""
        self._camera_manager.save_photo()
