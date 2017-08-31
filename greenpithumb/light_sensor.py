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

    def light(self):
        """Returns light level as percentage.

        Raises:
            LightSensorLowError: Ambient light level is lower than the minimum
                expected value.
        """
        light = self._adc.read_adc(self._channel)
        logger.info('light reading = %d', light)

        if light < _LIGHT_SENSOR_MIN_VALUE:
            raise LightSensorLowError(
                ('Light sensor reading of %i is less than the minimum '
                 'expected value of %i.') % (light, _LIGHT_SENSOR_MIN_VALUE))

        light_as_pct = 100 * (float(light - _LIGHT_SENSOR_MIN_VALUE) / (
            _LIGHT_SENSOR_MAX_VALUE - _LIGHT_SENSOR_MIN_VALUE))

        return light_as_pct
