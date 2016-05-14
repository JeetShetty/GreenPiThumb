import dht11_exceptions


class TemperatureSensor(object):
    """Wrapper for temperature sensor."""

    def __init__(self, dht11):
        """Creates a new TemperatureSensor wrapper.

        Args:
            dht11: Instance of DHT11 sensor reader class. 
        """
        self._dht11 = dht11

    def get_temperature(self):
        """Returns ambient temperature in Celcius."""
        dht11_result = self._dht11.read()
        error_code = dht11_result.error_code

        # TODO(JeetShetty): Replace error codes with constants from dht11 
        # module
        if error_code != 0:
            if error_code == 1:
                raise dht11_exceptions.MissingDataError(
                    "DHT11 sensor reported missing data")
            elif error_code == 2:
                raise dht11_exceptions.IncorrectCRCError(
                    "DHT11 sensor reported incorrect CRC")
            else:
                raise ValueError("DHT11 error code out of range: %i" %
                                 error_code)

        return dht11_result.temperature
