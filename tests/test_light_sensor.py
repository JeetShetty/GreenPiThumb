from __future__ import absolute_import
import unittest

import mock

from greenpithumb import adc
from greenpithumb import light_sensor


class LightSensorTest(unittest.TestCase):

    def setUp(self):
        self.mock_adc = mock.Mock(spec=adc.Adc)
        self.light_sensor = light_sensor.LightSensor(self.mock_adc)

    def test_light_50_pct(self):
        """Near midpoint light sensor value should return near 50."""
        self.mock_adc.read_pin.return_value = 656
        light_level = self.light_sensor.get_light_level()
        self.assertAlmostEqual(light_level, 49.93178718)

    def test_light_level_too_low(self):
        """Light sensor value less than min should raise a ValueError."""
        with self.assertRaises(light_sensor.LightSensorLowError):
            self.mock_adc.read_pin.return_value = (
                light_sensor._LIGHT_SENSOR_MIN_VALUE - 1)
            self.light_sensor.get_light_level()
