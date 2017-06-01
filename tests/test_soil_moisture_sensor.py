import collections
import unittest

import mock

from greenpithumb import soil_moisture_sensor


class MoistureSensorTest(unittest.TestCase):

    def setUp(self):
        self.mock_adc = mock.Mock()
        self.pin_state = collections.defaultdict(lambda: False)

        def mock_turn_pin_on(pin):
            self.pin_state[pin] = True

        def mock_turn_pin_off(pin):
            self.pin_state[pin] = False

        self.mock_pi_io = mock.Mock()
        self.mock_pi_io.turn_pin_on.side_effect = mock_turn_pin_on
        self.mock_pi_io.turn_pin_off.side_effect = mock_turn_pin_off

    def test_moisture_read_succeeds_when_adc_succeeds(self):
        self.mock_adc.read_adc.return_value = 350
        channel = 1
        gpio_pin = 12
        sensor = soil_moisture_sensor.SoilMoistureSensor(
            self.mock_adc, self.mock_pi_io, channel, gpio_pin)

        self.assertEqual(350, sensor.soil_moisture())
        self.mock_pi_io.turn_pin_on.assert_called_once_with(12)
        self.mock_pi_io.turn_pin_off.assert_called_once_with(12)
        self.assertFalse(self.pin_state[12])

    def test_moisture_sensor_pins_turned_off_if_adc_raises_exception(self):
        self.mock_adc.read_adc.side_effect = ValueError()
        channel = 1
        gpio_pin = 12
        sensor = soil_moisture_sensor.SoilMoistureSensor(
            self.mock_adc, self.mock_pi_io, channel, gpio_pin)

        with self.assertRaises(ValueError):
            sensor.soil_moisture()

        self.assertFalse(self.pin_state[12])
