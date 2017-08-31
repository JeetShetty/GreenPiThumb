import datetime
import unittest

from greenpithumb import sleep_windows


class TestSleepWindowParser(unittest.TestCase):

    def test_parser_valid_inputs(self):
        self.assertEqual(
            sleep_windows.parse(['01:00-03:15']), [(datetime.time(1, 0),
                                                    datetime.time(3, 15))])
        self.assertEqual(
            sleep_windows.parse(['01:00-03:15', '13:45-16:00']),
            [(datetime.time(1, 0), datetime.time(3, 15)), (datetime.time(
                13, 45), datetime.time(16, 0))])
        # Overlapping ranges OK.
        self.assertEqual(
            sleep_windows.parse(['01:00-03:15', '02:45-04:00']),
            [(datetime.time(1, 0), datetime.time(3, 15)),
             (datetime.time(2, 45), datetime.time(4, 0))])
        # Subset ranges OK.
        self.assertEqual(
            sleep_windows.parse(['01:00-03:15', '02:45-03:00']),
            [(datetime.time(1, 0), datetime.time(3, 15)),
             (datetime.time(2, 45), datetime.time(3, 0))])
        # Hypersomnia OK.
        self.assertEqual(
            sleep_windows.parse(['01:42-01:42']), [(datetime.time(1, 42),
                                                    datetime.time(1, 42))])

    def test_parser_invalid_inputs(self):
        invalid_inputs = [
            [''],  # empty string
            ['23:15-24:15'],  # invalid hour
            ['23:56-23:60'],  # invalid minute
            ['MickeyGates'],  # gibberish
            ['01:00-0300'],  # missing colon
            ['01:00-'],  # incomplete
            ['100:50-03:00'],  # invalid hour
            ['10:500-12:00'],  # invalid minute
            ['05:00:09.897-06:00'],  # unsupported seconds-level precision
            ['01:15-03:45sq']  # additional characters at end of window
        ]
        for invalid_input in invalid_inputs:
            with self.assertRaises(sleep_windows.InvalidWindowFormatError):
                sleep_windows.parse(invalid_input)
