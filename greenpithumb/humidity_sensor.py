class HumiditySensor(object):
    """Wrapper for a humidity sensor."""

    def __init__(self, dht11):
        """Creates a new HumiditySensor wrapper.

        Args:
            dht11: DHT11 sensor instance that returns relative humidity
                readings.
        """
        self._dht11 = dht11

    def get_humidity_level(self):
        """Returns relative humidity level."""
        return self._dht11.humidity()
