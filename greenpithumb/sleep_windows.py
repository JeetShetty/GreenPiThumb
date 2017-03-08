"""Parses sleep window strings."""

import datetime
import re


class Error(Exception):
    pass


class InvalidWindowFormatError(Error):
    pass


def parse(sleep_windows_raw):
    """Converts sleep windows from strings to datetime objects.

    Args:
        sleep_windows_raw: A list of sleep window strings. Each sleep window
            should be in 24-hour HH:MM-HH:MM format.

    Returns:
        A list of 2-tuples, each representing a sleep window. Tuple items
        are datetime.time objects.
    """
    sleep_windows = []
    for sleep_window in sleep_windows_raw:
        window_match = re.match(r'(\d\d):(\d\d)-(\d\d):(\d\d)$', sleep_window)
        if not window_match:
            raise InvalidWindowFormatError(
                'Sleep windows must be in 24-hour HH:MM-HH:MM format')
        try:
            sleep_time = datetime.time(
                int(window_match.group(1)), int(window_match.group(2)))
            wake_time = datetime.time(
                int(window_match.group(3)), int(window_match.group(4)))
        except ValueError:
            raise InvalidWindowFormatError(
                'Sleep windows must be in 24-hour HH:MM-HH:MM format')
        sleep_windows.append((sleep_time, wake_time))

    return sleep_windows
