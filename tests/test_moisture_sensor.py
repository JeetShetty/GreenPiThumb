from __future__ import absolute_import
import unittest

import mock

from greenpithumb import adc
from greenpithumb import moisture_sensor

class MoistureSensorTest(unittest.TestCase):

	def setUp(self):
		self.mock_adc = mock.Mock(spec=adc.Adc)
		self.moisture_sensor = moisture_sensor.MoistureSensor(self.mock_adc)

	def test_moisture_50(self):
		"""Moisture level read should be moisture level returned."""

		self.mock_adc.read_pin.return_value = 50.0 
		moisture_level = self.moisture_sensor.moisture()
		self.assertEqual(moisture_level, 50.0)


	def test_moisture_too_low_raises_ValueError(self):

		with self.assertRaises(ValueError):
			self.mock_adc.read_pin.return_value = (
				moisture_sensor._MIN_MOISTURE_LEVEL - 1)
			self.moisture_sensor.moisture()

	def test_moisture_too_high_raises_ValueError(self):

		with self.assertRaises(ValueError):
			self.mock_adc.read_pin.return_value = (
				moisture_sensor._MAX_MOISTURE_LEVEL + 1)
			self.moisture_sensor.moisture()
