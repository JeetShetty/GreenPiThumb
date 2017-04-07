import collections
import unittest

import mock

from greenpithumb import moisture_sensor


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
        self.mock_clock = mock.Mock()

    def test_moisture_read_succeeds_when_adc_succeeds(self):
        """Moisture level read should be the average of the two readings."""
        self.mock_adc.read_adc.side_effect = [300, (1023 - 400)]
        channel = 1
        gpio_pin_1 = 12
        gpio_pin_2 = 16
        sensor = moisture_sensor.MoistureSensor(self.mock_adc, self.mock_pi_io,
                                                channel, gpio_pin_1, gpio_pin_2,
                                                self.mock_clock)

        self.assertEqual(350, sensor.moisture())
        self.assertEqual([mock.call(12), mock.call(16)],
                         self.mock_pi_io.turn_pin_on.call_args_list)
        self.assertEqual([
            mock.call(16), mock.call(12), mock.call(12), mock.call(12),
            mock.call(16)
        ], self.mock_pi_io.turn_pin_off.call_args_list)
        self.assertFalse(self.pin_state[12])
        self.assertFalse(self.pin_state[16])
        self.mock_clock.wait.assert_called_once_with(0.1)

    def test_moisture_sensor_pins_turned_off_if_adc_raises_exception(self):
        self.mock_adc.read_adc.side_effect = ValueError()
        channel = 1
        gpio_pin_1 = 12
        gpio_pin_2 = 16
        sensor = moisture_sensor.MoistureSensor(self.mock_adc, self.mock_pi_io,
                                                channel, gpio_pin_1, gpio_pin_2,
                                                self.mock_clock)

        with self.assertRaises(ValueError):
            sensor.moisture()

        self.assertFalse(self.pin_state[12])
        self.assertFalse(self.pin_state[16])
