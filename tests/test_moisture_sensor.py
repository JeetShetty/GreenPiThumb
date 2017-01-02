import unittest

import mock

from greenpithumb import moisture_sensor


class MoistureSensorTest(unittest.TestCase):

    def setUp(self):
        self.mock_adc = mock.Mock()
        channel = 1
        self.moisture_sensor = moisture_sensor.MoistureSensor(self.mock_adc,
                                                              channel)

    def test_moisture_50(self):
        """Moisture level read should be moisture level returned."""
        self.mock_adc.read_adc.return_value = 50
        moisture_level = self.moisture_sensor.moisture()
        self.assertEqual(moisture_level, 50)
