import unittest

import mock

from greenpithumb import adc
from greenpithumb import weight_sensor


class WeightSensorTest(unittest.TestCase):

    def setUp(self):
        self.mock_adc = mock.Mock(spec=adc.Adc)
        self.weight_sensor = weight_sensor.WeightSensor(self.mock_adc)

    def test_weight_500(self):
        """Weight returned should be weight read."""
        self.mock_adc.read_pin.return_value = 500
        weight = self.weight_sensor.weight()
        self.assertEqual(weight, 500)
