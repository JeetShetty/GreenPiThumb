import unittest

import mock

from greenpithumb import light_sensor


class LightSensorTest(unittest.TestCase):

    def setUp(self):
        self.mock_adc = mock.Mock()
        channel = 1
        self.light_sensor = light_sensor.LightSensor(self.mock_adc, channel)

    def test_light_50_pct(self):
        """Near midpoint light sensor value should return near 50."""
        self.mock_adc.read_adc.return_value = 511
        self.assertAlmostEqual(self.light_sensor.light(), 50.0, places=1)

    def test_ambient_light_too_low(self):
        """Light sensor value less than min should raise a ValueError."""
        with self.assertRaises(light_sensor.LightSensorLowError):
            self.mock_adc.read_adc.return_value = (
                light_sensor._LIGHT_SENSOR_MIN_VALUE - 1)
            self.light_sensor.light()
