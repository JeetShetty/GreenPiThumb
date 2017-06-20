import datetime
import time
import unittest

import mock
import pytz

from greenpithumb import clock


class ClockTest(unittest.TestCase):

    def setUp(self):
        self.clock = clock.Clock()

    @mock.patch.object(time, 'sleep')
    def test_wait_waits_for_correct_number_of_milliseconds(self, mock_sleep):
        self.clock.wait(5.0)
        mock_sleep.assert_called_once_with(5.0)

    @mock.patch.object(time, 'sleep')
    def test_zero_wait_time(self, mock_sleep):
        """Waiting zero seconds is valid."""
        self.clock.wait(0.0)
        mock_sleep.assert_called_once_with(0.0)

    def test_negative_numbers_raise_ValueError(self):
        """Waiting a negative time is invalid and should raise an exception."""
        with self.assertRaises(ValueError):
            self.clock.wait(-1.0)

    def test_now_is_timezone_aware(self):
        """now() should always return a tz-aware datetime."""
        self.assertIsNotNone(self.clock.now().tzinfo)


class TimerTest(unittest.TestCase):

    def setUp(self):
        self.mock_clock = mock.Mock()

    def test_timer_duration_exceeded(self):
        duration = datetime.timedelta(hours=3 * 24)
        self.mock_clock.now.side_effect = [
            datetime.datetime(
                2000, 1, 1, 0, 0, 0, 0, tzinfo=pytz.utc),
            datetime.datetime(
                2000, 1, 5, 0, 0, 0, 0, tzinfo=pytz.utc)
        ]  # yapf: disable
        self.assertTrue(clock.Timer(self.mock_clock, duration).expired())

    def test_timer_duration_matched(self):
        duration = datetime.timedelta(hours=3 * 24)
        self.mock_clock.now.side_effect = [
            datetime.datetime(
                2000, 1, 1, 0, 0, 0, 0, tzinfo=pytz.utc),
            datetime.datetime(
                2000, 1, 4, 0, 0, 0, 0, tzinfo=pytz.utc)
        ]  # yapf: disable
        self.assertTrue(clock.Timer(self.mock_clock, duration).expired())

    def test_timer_duration_not_matched_or_exceeded(self):
        duration = datetime.timedelta(hours=3 * 24)
        self.mock_clock.now.side_effect = [
            datetime.datetime(
                2000, 1, 1, 0, 0, 0, 0, tzinfo=pytz.utc),
            datetime.datetime(
                2000, 1, 3, 0, 0, 0, 0, tzinfo=pytz.utc)
        ]  # yapf: disable
        self.assertFalse(clock.Timer(self.mock_clock, duration).expired())

    def test_set_remaining_fails_when_remaining_is_longer_than_duration(self):
        duration = datetime.timedelta(days=3)
        self.mock_clock.now.return_value = datetime.datetime(
            2000, 1, 1, 0, 0, 0, 0, tzinfo=pytz.utc)
        timer = clock.Timer(self.mock_clock, duration)
        with self.assertRaises(ValueError):
            timer.set_remaining(datetime.timedelta(days=4))

    def test_set_remaining_fails_when_remaining_is_negative(self):
        duration = datetime.timedelta(days=3)
        self.mock_clock.now.return_value = datetime.datetime(
            2000, 1, 1, 0, 0, 0, 0, tzinfo=pytz.utc)
        timer = clock.Timer(self.mock_clock, duration)
        with self.assertRaises(ValueError):
            timer.set_remaining(datetime.timedelta(days=-1))

    def test_set_remaining_succeeds_when_remaining_is_zero(self):
        duration = datetime.timedelta(days=3)
        self.mock_clock.now.return_value = datetime.datetime(
            2000, 1, 1, 0, 0, 0, 0, tzinfo=pytz.utc)
        timer = clock.Timer(self.mock_clock, duration)
        timer.set_remaining(datetime.timedelta(seconds=0))
        self.assertTrue(timer.expired())

    def test_set_remaining_succeeds_when_remaining_equals_duration(self):
        duration = datetime.timedelta(days=3)
        self.mock_clock.now.return_value = datetime.datetime(
            2000, 1, 1, 0, 0, 0, 0, tzinfo=pytz.utc)
        timer = clock.Timer(self.mock_clock, duration)
        timer.set_remaining(datetime.timedelta(days=3))
        self.mock_clock.now.return_value = datetime.datetime(
            2000, 1, 3, 23, 59, 59, 999999, tzinfo=pytz.utc)
        self.assertFalse(timer.expired())
        self.mock_clock.now.return_value = datetime.datetime(
            2000, 1, 4, 0, 0, 0, 0, tzinfo=pytz.utc)
        self.assertTrue(timer.expired())

    def test_set_remaining_succeeds_when_remaining_is_less_than_duration(self):
        duration = datetime.timedelta(days=3)
        self.mock_clock.now.return_value = datetime.datetime(
            2000, 1, 1, 0, 0, 0, 0, tzinfo=pytz.utc)
        timer = clock.Timer(self.mock_clock, duration)
        timer.set_remaining(datetime.timedelta(days=1))
        self.mock_clock.now.return_value = datetime.datetime(
            2000, 1, 1, 23, 59, 59, 999999, tzinfo=pytz.utc)
        self.assertFalse(timer.expired())
        self.mock_clock.now.return_value = datetime.datetime(
            2000, 1, 2, 0, 0, 0, 0, tzinfo=pytz.utc)
        self.assertTrue(timer.expired())

    def test_reset(self):
        duration = datetime.timedelta(hours=3 * 24)
        self.mock_clock.now.return_value = datetime.datetime(
            2000, 1, 1, 0, 0, 0, 0, tzinfo=pytz.utc)
        timer = clock.Timer(self.mock_clock, duration)
        self.mock_clock.now.return_value = datetime.datetime(
            2000, 1, 2, 0, 0, 0, 0, tzinfo=pytz.utc)
        timer.reset()
        self.mock_clock.now.return_value = datetime.datetime(
            2000, 1, 4, 23, 59, 59, 999999, tzinfo=pytz.utc)
        # First expired call is one microsecond before when the timer should
        # expire, second is right when it should expire.
        self.assertFalse(timer.expired())
        self.mock_clock.now.return_value = datetime.datetime(
            2000, 1, 5, 0, 0, 0, 0, tzinfo=pytz.utc)
        self.assertTrue(timer.expired())
