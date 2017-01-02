from __future__ import absolute_import
import unittest

import mock

from greenpithumb import pi_io


class IOTest(unittest.TestCase):

    def test_turn_pin_on(self):
        mock_GPIO = mock.Mock()
        io = pi_io.IO(mock_GPIO)
        pin = 1
        io.turn_pin_on(pin)
        mock_GPIO.setup.assert_called_once_with(pin, mock_GPIO.OUT)
        mock_GPIO.output.assert_called_once_with(pin, mock_GPIO.HIGH)

    def test_turn_pin_off(self):
        mock_GPIO = mock.Mock()
        io = pi_io.IO(mock_GPIO)
        pin = 1
        io.turn_pin_off(pin)
        mock_GPIO.setup.assert_called_once_with(pin, mock_GPIO.OUT)
        mock_GPIO.output.assert_called_once_with(pin, mock_GPIO.LOW)

    def test_setup_only_called_once_per_pin(self):
        mock_GPIO = mock.Mock()
        io = pi_io.IO(mock_GPIO)
        pin_one = 1
        pin_two = 2
        io.turn_pin_on(pin_one)
        io.turn_pin_on(pin_two)
        io.turn_pin_off(pin_one)
        io.turn_pin_on(pin_one)
        io.turn_pin_off(pin_two)
        io.turn_pin_on(pin_two)

        self.assertEqual(mock_GPIO.setup.call_args_list,
                         [((pin_one, mock_GPIO.OUT),),
                          ((pin_two, mock_GPIO.OUT),)])

    def test_close(self):
        mock_GPIO = mock.Mock()
        io = pi_io.IO(mock_GPIO)
        io.close()
        mock_GPIO.cleanup.assert_called_once()
