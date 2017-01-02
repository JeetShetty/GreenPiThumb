class MoistureSensor(object):
    """Wrapper for DHT11 moisture sensor."""

    def __init__(self, adc, channel):
        """Creates a new MoistureSensor wrapper.

        Args:
            adc: ADC(analog to digital) interface to receive analog signals from
                moisture sensor.
            channel: ADC channel to which the moisture sensor is connected.
        """
        self._adc = adc
        self._channel = channel

    def moisture(self):
        """Returns moisture level."""
        return self._adc.read_adc(self._channel)
