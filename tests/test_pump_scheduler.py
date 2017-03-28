import datetime
import unittest

import mock
import pytz

from greenpithumb import pump_scheduler


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
        pump_sched = pump_scheduler.PumpScheduler(self.mock_local_clock,
                                                  sleep_windows)
        self.assertFalse(pump_sched.is_running_pump_allowed())

    def test_wake_time_greater_than_sleep_time(self):
        self.mock_local_clock.now.return_value = (datetime.datetime(
            2016, 7, 23, 10, 51, 9, 928000, tzinfo=pytz.utc))
        sleep_windows = [(datetime.time(5, 23), datetime.time(14, 15))]
        pump_sched = pump_scheduler.PumpScheduler(self.mock_local_clock,
                                                  sleep_windows)
        self.assertFalse(pump_sched.is_running_pump_allowed())

    def test_multiple_sleep_windows(self):
        """Pump should not run if current hour is in any sleep window."""
        self.mock_local_clock.now.return_value = (datetime.datetime(
            2016, 7, 23, 10, 51, 9, 928000, tzinfo=pytz.utc))
        sleep_windows = [(datetime.time(16, 30), datetime.time(20, 45)),
                         (datetime.time(8, 13), datetime.time(11, 18))]
        pump_sched = pump_scheduler.PumpScheduler(self.mock_local_clock,
                                                  sleep_windows)
        self.assertFalse(pump_sched.is_running_pump_allowed())

    def test_running_pump_allowed_if_not_in_sleep_window(self):
        self.mock_local_clock.now.return_value = (datetime.datetime(
            2016, 7, 23, 10, 51, 9, 928000, tzinfo=pytz.utc))
        sleep_windows = [(datetime.time(2, 11), datetime.time(8, 33))]
        pump_sched = pump_scheduler.PumpScheduler(self.mock_local_clock,
                                                  sleep_windows)
        self.assertTrue(pump_sched.is_running_pump_allowed())

    def test_current_hour_and_minute_equal_to_sleep_time(self):
        """Running pump should not be allowed."""
        now = datetime.datetime(2016, 7, 23, 10, 51, 9, 928000, tzinfo=pytz.utc)
        self.mock_local_clock.now.return_value = now
        sleep_windows = [(datetime.time(now.hour, now.minute),
                          datetime.time(11, 0))]
        pump_sched = pump_scheduler.PumpScheduler(self.mock_local_clock,
                                                  sleep_windows)
        self.assertFalse(pump_sched.is_running_pump_allowed())

    def test_current_hour_and_minute_equal_to_wake_time(self):
        """Running pump should be allowed."""
        now = datetime.datetime(2016, 7, 23, 10, 51, 9, 928000, tzinfo=pytz.utc)
        self.mock_local_clock.now.return_value = now
        sleep_windows = [(datetime.time(10, 0), datetime.time(now.hour,
                                                              now.minute))]
        pump_sched = pump_scheduler.PumpScheduler(self.mock_local_clock,
                                                  sleep_windows)
        self.assertTrue(pump_sched.is_running_pump_allowed())
