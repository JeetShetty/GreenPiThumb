from __future__ import absolute_import
import time
import unittest

import mock

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
