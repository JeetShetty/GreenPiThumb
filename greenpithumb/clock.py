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


class Timer(object):
    """A countdown timer."""

    def __init__(self, clock, duration):
        """Creates a new timer.

        Args:
            clock: A clock interface.
            duration: A datetime timedelta of the countdown duration.
        """
        self._clock = clock
        self._duration = duration
        self.reset()

    def set_remaining(self, time_remaining):
        """Adjusts the remaining time on the timer.

        Args:
            time_remaining: The new amount of time remaining before the timer
                expires. Must be a timedelta between 0 seconds and the timer
                duration (inclusive).

        Raises:
            ValueError if time_remaining is a negative timedelta or is longer
            than the timer's duration.
        """
        if time_remaining < datetime.timedelta(seconds=0):
            raise ValueError('time_remaining must be non-negative')
        if time_remaining > self._duration:
            raise ValueError(
                'Cannot set time_remaining to longer than duration')
        self._end_time = self._clock.now() + time_remaining

    def expired(self):
        """Returns True if the countdown has expired."""
        return self._clock.now() >= self._end_time

    def reset(self):
        """Resets the countdown timer to its starting duration."""
        self._end_time = self._clock.now() + self._duration
