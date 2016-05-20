import dht11_exceptions

from dht11 import dht11


class HumiditySensor(object):
    """Wrapper for humidity sensor. Wraps DHT11 sensor."""

    def __init__(self, dht11):
        """Creates a new HumiditySensor wrapper.

        Args:
            dht11: Instance of DHT11 sensor reader class.
        """
        self._dht11 = dht11

    def get_humidity_level(self):
        """Returns humidity level."""
        dht11_result = self._dht11.read()
        error_code = dht11_result.error_code

        if error_code != dht11.DHT11Result.ERR_NO_ERROR:
            if error_code == dht11.DHT11Result.ERR_MISSING_DATA:
                raise dht11_exceptions.MissingDataError(
                    "DHT11 sensor reported missing data")
            elif error_code == dht11.DHT11Result.ERR_CRC:
                raise dht11_exceptions.IncorrectCRCError(
                    "DHT11 sensor reported incorrect CRC")
            else:
                raise ValueError("DHT11 error code out of range: %i" %
                                 error_code)

        return dht11_result.humidity
