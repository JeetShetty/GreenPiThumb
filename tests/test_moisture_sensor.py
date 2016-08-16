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
        self.mock_adc.read_pin.return_value = 50
        moisture_level = self.moisture_sensor.moisture()
        self.assertEqual(moisture_level, 50)
