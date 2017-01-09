import unittest

import mock

from greenpithumb import clock
from greenpithumb import pump


class PumpTest(unittest.TestCase):

    def setUp(self):
        self.mock_pi_io = mock.Mock()
        self.mock_clock = mock.Mock(spec=clock.Clock)

    def test_pump_4_3_liters(self):
        pump.Pump(
            self.mock_pi_io, self.mock_clock, pump_pin=6).pump_water(4300.0)
        # Pump should call wait() exactly once.
        self.assertEqual(1, len(self.mock_clock.wait.call_args_list))
        wait_time_actual = self.mock_clock.wait.call_args[0][0]
        # At 4.3 L/min, pump should run for exactly 60 seconds.
        wait_time_expected = 60.0
        # There is loss of precision with floating point arithmetic, so we
        # verify that the values are equal to several significant digits.
        self.assertAlmostEqual(wait_time_expected, wait_time_actual)
        # Verify the signal gets sent to turn the pump pin on, then off.
        self.mock_pi_io.turn_pin_on.assert_called_once_with(6)
        self.mock_pi_io.turn_pin_off.assert_called_once_with(6)

    def test_pump_2_15_liters(self):
        pump.Pump(
            self.mock_pi_io, self.mock_clock, pump_pin=6).pump_water(2150.0)
        # Pump should call wait() exactly once.
        self.assertEqual(1, len(self.mock_clock.wait.call_args_list))
        wait_time_actual = self.mock_clock.wait.call_args[0][0]
        # At 4.3 L/min, pump should run for exactly 30 seconds.
        wait_time_expected = 30.0
        # There is loss of precision with floating point arithmetic, so we
        # verify that the values are equal to several significant digits.
        self.assertAlmostEqual(wait_time_expected, wait_time_actual)
        # Verify the signal gets sent to turn the pump pin on, then off.
        # off.
        self.mock_pi_io.turn_pin_on.assert_called_once_with(6)
        self.mock_pi_io.turn_pin_off.assert_called_once_with(6)

    def test_pump_zero_does_not_turn_on_pump(self):
        """Pumping zero milliliters is allowed, but should not turn on pump."""
        pump.Pump(self.mock_pi_io, self.mock_clock, 6).pump_water(0.0)
        self.assertFalse(self.mock_pi_io.turn_pin_on.called)
        self.assertFalse(self.mock_clock.wait.called)
        self.assertFalse(self.mock_pi_io.turn_pin_off.called)

    def test_pump_negative_amount_raises_ValueError(self):
        """Attempting to pump a negative amount of water raises an exception."""
        with self.assertRaises(ValueError):
            pump.Pump(self.mock_pi_io, self.mock_clock, 6).pump_water(-5.0)
