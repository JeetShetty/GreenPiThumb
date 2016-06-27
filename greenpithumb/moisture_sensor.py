import adc


class MoistureSensor(object):
    """Wrapper for DHT11 moisture sensor."""

    def __init__(self, adc):
        """Creates a new MoistureSensor wrapper.

        Args:
            adc: ADC(analog to digital) interface to receive analog signals from
                moisture sensor.
        """
        self._adc = adc

    def moisture(self):
        """Returns moisture level."""
        return self._adc.read_pin(adc.PIN_MOISTURE_SENSOR)
