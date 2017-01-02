class WeightSensor(object):
    """Wrapper for a weight sensor."""

    def __init__(self, adc, channel):
        """Creates a new WeightSensor wrapper.

        Args:
            adc: ADC(analog to digital) interface to receive analog signals
                from weight sensor.
            channel: ADC channel to which the weight sensor is connected.
        """
        self._adc = adc
        self._channel = channel

    def weight(self):
        """Returns weight in grams."""
        weight = self._adc.read_adc(self._channel)

        # TODO(JeetShetty): Implement the actual conversion from weight to
        # weight_grams
        weight_grams = weight

        return weight_grams
