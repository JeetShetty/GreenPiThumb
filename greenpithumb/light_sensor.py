import logging

logger = logging.getLogger(__name__)

_LIGHT_SENSOR_MIN_VALUE = 0
_LIGHT_SENSOR_MAX_VALUE = 1023


class Error(Exception):
    pass


class LightSensorLowError(Error):
    pass


class LightSensor(object):
    """Wrapper for light sensor."""

    def __init__(self, adc, channel):
        """Creates a new LightSensor wrapper.

        Args:
            adc: ADC(analog to digital) interface to receive
                analog signals from light sensor.
            channel: ADC channel to which the light sensor is connected.
        """
        self._adc = adc
        self._channel = channel

    def ambient_light(self):
        """Returns light level as percentage.

        Raises:
            LightSensorLowError: Ambient light level is lower than the minimum
                expected value.
        """
        ambient_light = self._adc.read_adc(self._channel)
        logger.info('ambient light reading = %d', ambient_light)

        if ambient_light < _LIGHT_SENSOR_MIN_VALUE:
            raise LightSensorLowError(
                ('Light sensor reading of %i is less than the minimum '
                 'expected value of %i.') % (ambient_light,
                                             _LIGHT_SENSOR_MIN_VALUE))

        ambient_light_as_pct = 100 * (
            float(ambient_light - _LIGHT_SENSOR_MIN_VALUE) /
            (_LIGHT_SENSOR_MAX_VALUE - _LIGHT_SENSOR_MIN_VALUE))

        return ambient_light_as_pct
