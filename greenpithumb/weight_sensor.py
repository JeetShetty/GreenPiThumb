import adc

MIN_WEIGHT = 0.0
_MAX_WEIGHT = 1023.0


class WeightSensor(object):
    """Wrapper for a weight sensor."""

    def __init__(self, adc):
        """Creates a new WeightSensor wrapper.

        Args:
            adc: ADC(analog to digital) interface to receive analog signals
                from weight sensor.
        """
        self._adc = adc

    def weight(self):
        """Returns weight in grams."""
        weight = self._adc.read_pin(adc.PIN_WEIGHT_SENSOR)
        if not MIN_WEIGHT <= weight <= _MAX_WEIGHT:
            raise ValueError('reservoir weight out of range: %.1f' % weight)

        # TODO(JeetShetty): Implement the actual conversion from weight to
        # weight_grams
        weight_grams = weight

        return weight_grams
