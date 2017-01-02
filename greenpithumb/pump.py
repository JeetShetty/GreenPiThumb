# Pump rate in mL/s (4.3 L/min)
_PUMP_RATE_ML_PER_SEC = 4300.0 / 60.0


class Pump(object):
    """Wrapper for a Seaflo 12V water pump."""

    def __init__(self, pi_io, clock, pump_pin):
        """Creates a new Pump wrapper.

        Args:
            pi_io: Raspberry Pi I/O interface.
            clock: A clock interface.
            pump_pin: Raspberry Pi pin to which the pump is connected.
        """
        self._pi_io = pi_io
        self._clock = clock
        self._pump_pin = pump_pin

    def pump_water(self, amount_ml):
        """Pumps the specified amount of water.

        Args:
            amount_ml: Amount of water to pump (in mL).

        Raises:
            ValueError: The amount of water to be pumped is invalid.
        """
        if amount_ml == 0.0:
            return
        elif amount_ml < 0.0:
            raise ValueError('Cannot pump a negative amount of water')
        else:
            self._pi_io.turn_pin_on(self._pump_pin)

            wait_time_seconds = amount_ml / _PUMP_RATE_ML_PER_SEC
            self._clock.wait(wait_time_seconds)

            self._pi_io.turn_pin_off(self._pump_pin)

        return
