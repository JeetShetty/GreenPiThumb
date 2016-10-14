import adc

_LIGHT_SENSOR_MIN_VALUE = 290
_LIGHT_SENSOR_MAX_VALUE = adc.PIN_MAX_VALUE


class Error(Exception):
    pass


class LightSensorLowError(Error):
    pass


class LightSensor(object):
    """Wrapper for light sensor."""

    def __init__(self, adc):
        """Creates a new LightSensor wrapper.

        Args:
            adc: ADC(analog to digital) interface to receive
                analog signals from light sensor.
        """
        self._adc = adc

    def ambient_light(self):
        """Returns light level as percentage."""
        ambient_light = self._adc.read_pin(adc.PIN_LIGHT_SENSOR)

        if ambient_light < _LIGHT_SENSOR_MIN_VALUE:
            raise LightSensorLowError(
                ('Light sensor reading of %i is less than the minimum '
                 'expected value of %i.') % (ambient_light,
                                             _LIGHT_SENSOR_MIN_VALUE))

        ambient_light_as_pct = 100 * (
            float(ambient_light - _LIGHT_SENSOR_MIN_VALUE) /
            (_LIGHT_SENSOR_MAX_VALUE - _LIGHT_SENSOR_MIN_VALUE))

        return ambient_light_as_pct
