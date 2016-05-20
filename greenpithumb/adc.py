# TODO(mtlynch): Move these pin constants to a configuration file so they're not
# hardcoded in.

# ADC pin to which water pump is connected
PIN_PUMP = 0
PIN_LIGHT_SENSOR = 1
PIN_MOISTURE_SENSOR = 2
PIN_HUMIDITY_SENSOR = 3

# Signal to turn an ADC pin off.
SIGNAL_OFF = 0

# Signal to turn an ADC pin on.
SIGNAL_ON = 1023


class Adc(object):
    """Wrapper for an MCP3008 analog to digital converter (ADC).

    This wraps the ADC and allows the caller to read or send digital signals to
    the ADC's eight I/O pins.
    """

    def read_pin(self, pin):
        """Reads a digital value from an ADC pin.

        Args:
            pin: Index of ADC pin to read from (must be an int between 0 and 7).

        Returns:
            The signal read from the ADC pin (an int between 0 and 1023).
        """
        raise NotImplementedError()

    def write_pin(self, pin, value):
        """Writes a digital value to an ADC pin.

        Args:
            pin: Index of ADC pin to write to (must be an int between 0 and 7).
            value: Value to write to the pin (must be an int between 0 and
                1023).
        """
        raise NotImplementedError()
