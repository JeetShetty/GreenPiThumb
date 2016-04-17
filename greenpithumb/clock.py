import time


class Clock(object):
    """An wrapper for managing clock time functions."""

    def wait(self, wait_time_seconds):
        """Wait for the specified number of milliseconds."""
        if wait_time_seconds < 0.0:
            raise ValueError(
                'Wait time cannot be negative: %f' % wait_time_seconds)
        time.sleep(wait_time_seconds)
