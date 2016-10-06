import threading


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

    def _poll_forever(self):
        """Polls, forever, at a fixed interval."""
        while True:
            self._poll_once()
            self._local_clock.wait(self._poll_interval)

    def start_polling_async(self):
        """Starts a new thread to begin polling."""
        t = threading.Thread(target=self._poll_forever)
        t.setDaemon(True)
        t.start()


class TemperaturePoller(SensorPollerBase):
    """Polls a temperature sensor and stores the readings."""

    def __init__(self, local_clock, poll_interval, temperature_sensor,
                 temperature_store):
        """Creates a new TemperaturePoller object.

        Args:
            local_clock: A local time zone clock interface.
            poll_interval: An int of how often the sensor should be polled, in
                seconds.
            temperature_sensor: An interface for reading the temperature.
            temperature_store: An interface for storing temperature readings.
        """
        super(TemperaturePoller, self).__init__(local_clock, poll_interval)
        self._temperature_sensor = temperature_sensor
        self._temperature_store = temperature_store

    def _poll_once(self):
        """Polls for and stores current ambient temperature."""
        temperature = self._temperature_sensor.get_temperature()
        self._temperature_store.store_temperature(self._local_clock.now(),
                                                  temperature)


class HumidityPoller(SensorPollerBase):
    """Polls a humidity sensor and stores the readings."""

    def __init__(self, local_clock, poll_interval, humidity_sensor,
                 humidity_store):
        """Creates a new HumidityPoller object.

        Args:
            local_clock: A local time zone clock interface.
            poll_interval: An int of how often the sensor should be polled, in
                seconds.
            humidity_sensor: An interface for reading the humidity.
            humidity_store: An interface for storing humidity readings.
        """
        super(HumidityPoller, self).__init__(local_clock, poll_interval)
        self._humidity_sensor = humidity_sensor
        self._humidity_store = humidity_store

    def _poll_once(self):
        """Polls for and stores current relative humidity."""
        humidity = self._humidity_sensor.get_humidity_level()
        self._humidity_store.store_humidity(self._local_clock.now(), humidity)


class MoisturePoller(SensorPollerBase):
    """Polls a moisture sensor and stores the readings."""

    def __init__(self, local_clock, poll_interval, moisture_sensor,
                 soil_moisture_store):
        """Creates a MoisturePoller object.

        Args:
            local_clock: A local time zone clock interface.
            poll_interval: An int of how often the sensor should be polled, in
                seconds.
            moisture_sensor: An interface for reading the moisture level.
            soil_moisture_store: An interface for storing moisture readings.
        """
        super(MoisturePoller, self).__init__(local_clock, poll_interval)
        self._moisture_sensor = moisture_sensor
        self._soil_moisture_store = soil_moisture_store

    def _poll_once(self):
        """Polls current soil moisture."""
        moisture = self._moisture_sensor.moisture()
        self._soil_moisture_store.store_soil_moisture(self._local_clock.now(),
                                                      moisture)


class AmbientLightPoller(SensorPollerBase):
    """Polls an ambient light sensor and stores the readings."""

    def __init__(self, local_clock, poll_interval, light_sensor,
                 ambient_light_store):
        """Creates a new AmbientLightPoller object.

        Args:
            local_clock: A local time zone clock interface.
            poll_interval: An int of how often the sensor should be polled, in
                seconds.
            light_sensor: An interface for reading the ambient light level.
            ambient_light_store: An interface for storing ambient light
                readings.
        """
        super(AmbientLightPoller, self).__init__(local_clock, poll_interval)
        self._light_sensor = light_sensor
        self._ambient_light_store = ambient_light_store

    def _poll_once(self):
        ambient_light = self._light_sensor.get_light_level()
        self._ambient_light_store.store_ambient_light(self._local_clock.now(),
                                                      ambient_light)


class ReservoirPoller(SensorPollerBase):
    """Polls for reservoir level data and stores the data."""

    def __init__(self, local_clock, poll_interval, reservoir,
                 reservoir_level_store):
        """Creates a new ReservoirPoller object.

        Args:
            local_clock: A local time zone clock interface.
            poll_interval: An int of how often the data should be polled for,
                in seconds.
            reservoir: An object that returns a reservoir level.
            reservoir_level_store: An interface for storing reservoir level
                readings.
        """
        super(ReservoirPoller, self).__init__(local_clock, poll_interval)
        self._reservoir = reservoir
        self._reservoir_level_store = reservoir_level_store

    def _poll_once(self):
        """Polls for and stores current reservoir level."""
        reservoir_level = self._reservoir.reservoir_level()
        self._reservoir_level_store.store_reservoir_level(
            self._local_clock.now(), reservoir_level)


class WateringEventPoller(SensorPollerBase):
    """Polls for and records watering event data.

    Polls for latest soil moisture readings and oversees a water pump based on
    those readings.
    """

    def __init__(self, local_clock, poll_interval, pump_manager,
                 watering_event_store, soil_moisture_store):
        """Creates a new WateringEventPoller object.

        Args:
            local_clock: A local time zone clock interface.
            poll_interval: An int of how often the data should be polled for,
                in seconds.
            pump_manager: An interface to manage a water pump.
            watering_event_store: An interface for storing watering event data.
            soil_moisture_store: An interface for storing and retrieving soil
                moisture readings.
        """
        super(WateringEventPoller, self).__init__(local_clock, poll_interval)
        self._pump_manager = pump_manager
        self._watering_event_store = watering_event_store
        self._soil_moisture_store = soil_moisture_store

    def _poll_once(self):
        """Oversees a water pump, and polls for and stores watering event data.

        Polls for latest soil moisture readings and feeds them to a water pump.
        If the pump runs, it stores the event data.
        """
        moisture = self._soil_moisture_store.get_latest_soil_moisture()
        if moisture is not None:
            ml_pumped = self._pump_manager.pump_if_needed(moisture)
            if ml_pumped > 0:
                self._watering_event_store.store_water_pumped(
                    self._local_clock.now(), ml_pumped)
