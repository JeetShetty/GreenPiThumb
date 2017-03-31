import threading


class Adc(object):
    """Thread-safe wrapper around an ADC object."""

    def __init__(self, adc):
        """Create a new Adc instance

        Args:
            adc: The raw ADC which this class makes thread-safe by synchronizing
                its read calls.
        """
        self._adc = adc
        self._lock = threading.Lock()

    def read_adc(self, adc_number):
        """Read a value from the ADC

        Args:
            adc_number: ADC channel to read.

        Returns:
            The value read from the given ADC channel (as a float).
        """
        with self._lock:
            return self._adc.read_adc(adc_number)
