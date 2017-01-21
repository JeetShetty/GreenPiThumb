import datetime
import unittest

import mock
import pytz

from greenpithumb import pump_scheduler


class PumpSchedulerTest(unittest.TestCase):

    def setUp(self):
        self.mock_clock = mock.Mock()

    def test_wake_hour_less_than_sleep_hour(self):
        """Test rollover from one day to the next.

        If the sleep period spans two days, the pump should not run between
        midnight and the wake hour.
        """
        self.mock_clock.now.return_value = datetime.datetime(
            2016, 5, 24, 0, tzinfo=pytz.utc)
        sleep_windows = [(22, 8)]
        pump_sched = pump_scheduler.PumpScheduler(self.mock_clock,
                                                  sleep_windows)
        self.assertFalse(pump_sched.is_running_pump_allowed())

    def test_wake_hour_greater_than_sleep_hour(self):
        self.mock_clock.now.return_value = datetime.datetime(
            2016, 5, 24, 4, tzinfo=pytz.utc)
        sleep_windows = [(2, 8)]
        pump_sched = pump_scheduler.PumpScheduler(self.mock_clock,
                                                  sleep_windows)
        self.assertFalse(pump_sched.is_running_pump_allowed())

    def test_multiple_sleep_windows(self):
        """Pump should not run if current hour is in any sleep window."""
        self.mock_clock.now.return_value = datetime.datetime(
            2016, 5, 24, 4, tzinfo=pytz.utc)
        sleep_windows = [(16, 20), (2, 8)]
        pump_sched = pump_scheduler.PumpScheduler(self.mock_clock,
                                                  sleep_windows)
        self.assertFalse(pump_sched.is_running_pump_allowed())

    def test_running_pump_allowed_if_not_in_sleep_window(self):
        self.mock_clock.now.return_value = datetime.datetime(
            2016, 5, 24, 10, tzinfo=pytz.utc)
        sleep_windows = [(2, 8)]
        pump_sched = pump_scheduler.PumpScheduler(self.mock_clock,
                                                  sleep_windows)
        self.assertTrue(pump_sched.is_running_pump_allowed())

    def test_current_hour_equal_to_sleep_hour(self):
        """Running pump should not be allowed."""
        self.mock_clock.now.return_value = datetime.datetime(
            2016, 5, 24, 2, tzinfo=pytz.utc)
        sleep_windows = [(2, 8)]
        pump_sched = pump_scheduler.PumpScheduler(self.mock_clock,
                                                  sleep_windows)
        self.assertFalse(pump_sched.is_running_pump_allowed())

    def test_current_hour_equal_to_wake_hour(self):
        """Running pump should be allowed."""
        self.mock_clock.now.return_value = datetime.datetime(
            2016, 5, 24, 8, tzinfo=pytz.utc)
        sleep_windows = [(2, 8)]
        pump_sched = pump_scheduler.PumpScheduler(self.mock_clock,
                                                  sleep_windows)
        self.assertTrue(pump_sched.is_running_pump_allowed())
