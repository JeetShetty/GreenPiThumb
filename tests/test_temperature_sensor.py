from __future__ import absolute_import
import unittest

import mock

from greenpithumb import temperature_sensor
from greenpithumb import dht11_exceptions


class TemperatureSensorTest(unittest.TestCase):

    def setUp(self):
        self.mock_dht11_result = mock.Mock()
        mock_dht11 = mock.Mock()
        mock_dht11.read.return_value = self.mock_dht11_result
        self.temperature_sensor = temperature_sensor.TemperatureSensor(
            mock_dht11)

    def test_humidity_50(self):
        """Value given should be value returned."""
        self.mock_dht11_result.error_code = 0
        self.mock_dht11_result.temperature = 50.0
        temperature = self.temperature_sensor.get_temperature()
        self.assertEqual(temperature, 50.0)

    def test_missing_data_error(self):
        """Error code of 1 should raise an exception."""
        with self.assertRaises(dht11_exceptions.MissingDataError):
            self.mock_dht11_result.error_code = 1
            self.temperature_sensor.get_temperature()

    def test_incorrect_crc_error(self):
        """Error code of 2 should raise an exception."""
        with self.assertRaises(dht11_exceptions.IncorrectCRCError):
            self.mock_dht11_result.error_code = 2
            self.temperature_sensor.get_temperature()

    def test_error_code_out_of_range(self):
        """Error code other than 0, 1, or 2 should raise an exception."""
        with self.assertRaises(ValueError):
            self.mock_dht11_result.error_code = 3
            self.temperature_sensor.get_temperature()
