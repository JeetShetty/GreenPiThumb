class PumpScheduler(object):
    """A wrapper for managing pump scheduling."""

    def __init__(self, clock, sleep_windows):
        """Creates new PumpScheduler wrapper.

        Args:
            clock: A clock interface
            sleep_windows: A tuple of tuples, each consisting of a sleep
                window. Time zone should match that of the clock interface.
        """
        self._clock = clock
        self._sleep_windows = sleep_windows

    def is_running_pump_allowed(self):
        """Returns True if OK to run pump, otherwise False."""
        current_hour = self._clock.now().hour

        for sleep_hour, wake_hour in self._sleep_windows:
            if wake_hour < sleep_hour:
                if current_hour >= sleep_hour or current_hour < wake_hour:
                    return False
            else:
                if sleep_hour <= current_hour < wake_hour:
                    return False

        return True
