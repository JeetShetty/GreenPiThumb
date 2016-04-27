import adc

_LIGHT_SENSOR_MAX_VALUE = 1023.0
_LIGHT_SENSOR_MIN_VALUE = 290.0

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

		if light_level < _LIGHT_SENSOR_MIN_VALUE or \
		light_level > _LIGHT_SENSOR_MAX_VALUE:
			raise ValueError('Light sensor reading out of range')

		light_level_as_pct = 100 * ((light_level - _LIGHT_SENSOR_MIN_VALUE) /
			(_LIGHT_SENSOR_MAX_VALUE - _LIGHT_SENSOR_MIN_VALUE))

		return light_level_as_pct