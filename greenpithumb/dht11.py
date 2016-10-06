import datetime
import threading

# Maximum time a sensor reading can be used for, in seconds
_FRESHNESS_THRESHOLD = 2
# Position of humidity value in the tuple returned from DHT11 read function.
_HUMIDITY_INDEX = 0
# Position of  temperature value in the tuple returned from DHT11 read function.
_TEMPERATURE_INDEX = 1


class CachingDHT11(object):
    """Wrapper around a DHT11 that caches sensor readings.

    Reads and returns temperature and humidity levels while also caching these
    values to ensure that the sensor is not polled at too high of a frequency.
    This class is thread-safe.
    """

    def __init__(self, dht11_read_func, clock):
        """Creates a new CachingDHT11 object.

        Args:
            dht11_read_func: A function that returns the temperature and
                humidity readings from a DHT11 sensor.
            clock: A clock interface
        """
        self._dht11_read_func = dht11_read_func
        self._clock = clock
        self._last_reading_time = datetime.datetime.min
        self._last_reading = None
        self._lock = threading.Lock()

    def _read_dht11(self):
        """Returns current or recent temperature and humidity values.

        Returns cached values if the sensor has been polled recently enough,
        otherwise polls the sensor and returns current values.
        """
        with self._lock:
            now = self._clock.now()
            if (now - self._last_reading_time).total_seconds() >= (
                    _FRESHNESS_THRESHOLD):
                self._last_reading_time = now
                self._last_reading = self._dht11_read_func()

        return self._last_reading

    def humidity(self):
        """Returns a recent relative humidity reading."""
        humidity = self._read_dht11()[_HUMIDITY_INDEX]
        return humidity

    def temperature(self):
        """Returns a recent ambient temperature reading in Celsius."""
        temperature = self._read_dht11()[_TEMPERATURE_INDEX]
        return temperature
