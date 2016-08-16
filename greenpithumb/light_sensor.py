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

    def get_light_level(self):
        """Returns light level as percentage."""
        light_level = self._adc.read_pin(adc.PIN_LIGHT_SENSOR)

        if light_level < _LIGHT_SENSOR_MIN_VALUE:
            raise LightSensorLowError(
                ('Light sensor reading of %i is less than the minimum '
                 'expected value of %i.') % (light_level,
                                             _LIGHT_SENSOR_MIN_VALUE))

        light_level_as_pct = 100 * (
            float(light_level - _LIGHT_SENSOR_MIN_VALUE) /
            (_LIGHT_SENSOR_MAX_VALUE - _LIGHT_SENSOR_MIN_VALUE))

        return light_level_as_pct
