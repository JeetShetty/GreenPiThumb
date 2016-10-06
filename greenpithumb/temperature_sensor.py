class TemperatureSensor(object):
    """Wrapper for a temperature sensor."""

    def __init__(self, dht11):
        """Creates a new TemperatureSensor wrapper.

        Args:
            dht11: DHT11 sensor instance that returns temperature readings.
        """
        self._dht11 = dht11

    def get_temperature(self):
        """Returns ambient temperature in Celcius."""
        return self._dht11.temperature()
