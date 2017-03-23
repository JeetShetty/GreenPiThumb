import logging

logger = logging.getLogger(__name__)


class TemperatureSensor(object):
    """Wrapper for a temperature sensor."""

    def __init__(self, dht11):
        """Creates a new TemperatureSensor wrapper.

        Args:
            dht11: DHT11 sensor instance that returns temperature readings.
        """
        self._dht11 = dht11

    def temperature(self):
        """Returns ambient temperature in Celcius."""
        temperature = self._dht11.temperature()
        logging.info('temperature reading = %.1f C', temperature)
        return temperature
