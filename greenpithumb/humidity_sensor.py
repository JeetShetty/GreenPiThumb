import logging

logger = logging.getLogger(__name__)


class HumiditySensor(object):
    """Wrapper for a humidity sensor."""

    def __init__(self, dht11):
        """Creates a new HumiditySensor wrapper.

        Args:
            dht11: DHT11 sensor instance that returns relative humidity
                readings.
        """
        self._dht11 = dht11

    def humidity(self):
        """Returns relative humidity level."""
        humidity = self._dht11.humidity()
        logger.info('humidity reading = %.1f', humidity)
        return humidity
