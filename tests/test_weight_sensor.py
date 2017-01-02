import unittest

import mock

from greenpithumb import weight_sensor


class WeightSensorTest(unittest.TestCase):

    def setUp(self):
        self.mock_adc = mock.Mock()
        channel = 1
        self.weight_sensor = weight_sensor.WeightSensor(self.mock_adc, channel)

    def test_weight_500(self):
        """Weight returned should be weight read."""
        self.mock_adc.read_adc.return_value = 500
        weight = self.weight_sensor.weight()
        self.assertEqual(weight, 500)
