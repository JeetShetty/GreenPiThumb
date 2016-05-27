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

        if amount_ml == 0.0:
            return
        elif amount_ml < 0.0:
            raise ValueError('Cannot pump a negative amount of water')
        else:
            self._adc.write_pin(0, 1023)

            wait_time_seconds = amount_ml / _PUMP_RATE_ML_PER_SEC
            self._clock.wait(wait_time_seconds)

            self._adc.write_pin(0, 0)

        return
