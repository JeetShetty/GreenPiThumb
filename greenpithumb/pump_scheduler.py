class PumpScheduler(object):
    """A wrapper for managing pump scheduling."""

    def __init__(self, local_clock, sleep_windows):
        """Creates new PumpScheduler wrapper.

        Args:
            local_clock: A local clock interface
            sleep_windows: A list of 2-tuples, each representing a sleep window.
                Tuple items are datetime.time objects.
        """
        self._local_clock = local_clock
        self._sleep_windows = sleep_windows

    def is_running_pump_allowed(self):
        """Returns True if OK to run pump, otherwise False.

        Pump is not allowed to run from the start of a sleep window (inclusive)
        to the end of a sleep window (exclusive).
        """
        current_time = self._local_clock.now().time()

        for sleep_time, wake_time in self._sleep_windows:
            # Check if sleep window wraps midnight.
            if wake_time < sleep_time:
                if current_time >= sleep_time or current_time < wake_time:
                    return False
            else:
                if sleep_time <= current_time < wake_time:
                    return False

        return True
