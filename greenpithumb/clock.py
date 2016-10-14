import datetime
import time

import pytz
import tzlocal


class Clock(object):
    """A wrapper for managing clock time functions."""

    def wait(self, wait_time_seconds):
        """Wait for the specified number of seconds.

        Args:
            wait_time_seconds: Number of seconds to wait.
        """
        if wait_time_seconds < 0.0:
            raise ValueError('Wait time cannot be negative: %f' %
                             wait_time_seconds)
        time.sleep(wait_time_seconds)

    def now(self):
        return datetime.datetime.now(tz=pytz.utc)


class LocalClock(Clock):
    """An implementation of Clock that operates in the local time zone."""

    def now(self):
        time_utc = super(LocalClock, self).now()
        return time_utc.astimezone(tzlocal.get_localzone())
