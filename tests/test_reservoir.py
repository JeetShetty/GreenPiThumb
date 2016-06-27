from __future__ import absolute_import
import unittest

import mock

from greenpithumb import weight_sensor
from greenpithumb import reservoir


class ReservoirTest(unittest.TestCase):

    def setUp(self):
        self.mock_weight_sensor = mock.Mock(spec=weight_sensor.WeightSensor)

    def test_water_level_in_range(self):
        self.mock_weight_sensor.weight.return_value = 55.0
        res = reservoir.Reservoir(self.mock_weight_sensor, 50.0)
        self.assertAlmostEqual(5.0, res.reservoir_level())

    def test_water_level_out_of_range(self):
        with self.assertRaises(reservoir.ReservoirUnderWeightError):
            container_weight = 50.0
            res = reservoir.Reservoir(self.mock_weight_sensor, container_weight)
            self.mock_weight_sensor.weight.return_value = container_weight - 1
            res.reservoir_level()
