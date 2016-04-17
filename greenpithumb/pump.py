import adc

# Pump rate in mL/s (4.3 L/min)
_PUMP_RATE_ML_PER_SEC = 4300.0 / 60.0


class Pump(object):
    """Wrapper for a Seaflo 12V water pump."""

    def __init__(self, adc, clock):
        """Creates a new Pump wrapper.

        Args:
            adc: ADC (analog to digital) interface to send digital signals to
                pump.
            clock: A clock interface.
        """
        self._adc = adc
        self._clock = clock

    def pump_water(self, amount_ml):
        """Pumps the specified amount of water.

        Args:
            amount_ml: Amount of water to pump (in mL).
        """
        # TODO(JeetShetty): Implement this.
        raise NotImplementedError()
