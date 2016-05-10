import adc

#placeholder values
_MIN_MOISTURE_LEVEL = 0.0
_MAX_MOISTURE_LEVEL = 1023.0


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
        moisture_level = self._adc.read_pin(adc.PIN_MOISTURE_SENSOR)

        if moisture_level < _MIN_MOISTURE_LEVEL or \
        moisture_level > _MAX_MOISTURE_LEVEL:
            raise ValueError('moisture level out of range: %.1f' %
                             moisture_level)

        return moisture_level
