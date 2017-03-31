import datetime
import unittest

import mock
import pytz

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


class PumpManagerTest(unittest.TestCase):

    def setUp(self):
        self.mock_pump = mock.Mock()
        self.mock_pump_scheduler = mock.Mock()
        self.manager = pump.PumpManager(self.mock_pump,
                                        self.mock_pump_scheduler)

    def test_low_moisture_triggers_pump(self):
        self.mock_pump_scheduler.is_running_pump_allowed.return_value = True
        moisture = pump.SOIL_MOISTURE_THRESHOLD - 100
        ml_pumped = self.manager.pump_if_needed(moisture)
        self.mock_pump.pump_water.assert_called_once_with(
            pump.DEFAULT_PUMP_AMOUNT)
        self.assertEqual(ml_pumped, pump.DEFAULT_PUMP_AMOUNT)

    def test_pump_not_triggered_if_moisture_is_at_threshold(self):
        self.mock_pump_scheduler.is_running_pump_allowed.return_value = True
        moisture = pump.SOIL_MOISTURE_THRESHOLD
        ml_pumped = self.manager.pump_if_needed(moisture)
        # Pump should not run if soil moisture is exactly at threshold.
        self.assertFalse(self.mock_pump.pump_water.called)
        self.assertEqual(ml_pumped, 0)

    def test_pump_not_triggered_if_moisture_is_high(self):
        self.mock_pump_scheduler.is_running_pump_allowed.return_value = True
        moisture = pump.SOIL_MOISTURE_THRESHOLD + 350
        ml_pumped = self.manager.pump_if_needed(moisture)
        # Pump should not run if soil moisture is above threshold.
        self.assertFalse(self.mock_pump.pump_water.called)
        self.assertEqual(ml_pumped, 0)

    def test_pump_is_disabled_during_quiet_hours(self):
        self.mock_pump_scheduler.is_running_pump_allowed.return_value = False
        moisture = pump.SOIL_MOISTURE_THRESHOLD - 100
        ml_pumped = self.manager.pump_if_needed(moisture)
        self.assertFalse(self.mock_pump.pump_water.called)
        self.assertEqual(ml_pumped, 0)


class PumpSchedulerTest(unittest.TestCase):

    def setUp(self):
        self.mock_local_clock = mock.Mock()

    def test_wake_time_less_than_sleep_time(self):
        """Test rollover from one day to the next.

        If the sleep period spans two days, the pump should not run between
        midnight and the wake hour.
        """
        self.mock_local_clock.now.return_value = (datetime.datetime(
            2016, 7, 23, 10, 51, 9, 928000, tzinfo=pytz.utc))
        sleep_windows = [(datetime.time(23, 0), datetime.time(11, 0))]
        pump_scheduler = pump.PumpScheduler(self.mock_local_clock,
                                            sleep_windows)
        self.assertFalse(pump_scheduler.is_running_pump_allowed())

    def test_wake_time_greater_than_sleep_time(self):
        self.mock_local_clock.now.return_value = (datetime.datetime(
            2016, 7, 23, 10, 51, 9, 928000, tzinfo=pytz.utc))
        sleep_windows = [(datetime.time(5, 23), datetime.time(14, 15))]
        pump_scheduler = pump.PumpScheduler(self.mock_local_clock,
                                            sleep_windows)
        self.assertFalse(pump_scheduler.is_running_pump_allowed())

    def test_multiple_sleep_windows(self):
        """Pump should not run if current hour is in any sleep window."""
        self.mock_local_clock.now.return_value = (datetime.datetime(
            2016, 7, 23, 10, 51, 9, 928000, tzinfo=pytz.utc))
        sleep_windows = [(datetime.time(16, 30), datetime.time(20, 45)),
                         (datetime.time(8, 13), datetime.time(11, 18))]
        pump_scheduler = pump.PumpScheduler(self.mock_local_clock,
                                            sleep_windows)
        self.assertFalse(pump_scheduler.is_running_pump_allowed())

    def test_running_pump_allowed_if_not_in_sleep_window(self):
        self.mock_local_clock.now.return_value = (datetime.datetime(
            2016, 7, 23, 10, 51, 9, 928000, tzinfo=pytz.utc))
        sleep_windows = [(datetime.time(2, 11), datetime.time(8, 33))]
        pump_scheduler = pump.PumpScheduler(self.mock_local_clock,
                                            sleep_windows)
        self.assertTrue(pump_scheduler.is_running_pump_allowed())

    def test_current_hour_and_minute_equal_to_sleep_time(self):
        """Running pump should not be allowed."""
        now = datetime.datetime(2016, 7, 23, 10, 51, 9, 928000, tzinfo=pytz.utc)
        self.mock_local_clock.now.return_value = now
        sleep_windows = [(datetime.time(now.hour, now.minute),
                          datetime.time(11, 0))]
        pump_scheduler = pump.PumpScheduler(self.mock_local_clock,
                                            sleep_windows)
        self.assertFalse(pump_scheduler.is_running_pump_allowed())

    def test_current_hour_and_minute_equal_to_wake_time(self):
        """Running pump should be allowed."""
        now = datetime.datetime(2016, 7, 23, 10, 51, 9, 928000, tzinfo=pytz.utc)
        self.mock_local_clock.now.return_value = now
        sleep_windows = [(datetime.time(10, 0), datetime.time(now.hour,
                                                              now.minute))]
        pump_scheduler = pump.PumpScheduler(self.mock_local_clock,
                                            sleep_windows)
        self.assertTrue(pump_scheduler.is_running_pump_allowed())
