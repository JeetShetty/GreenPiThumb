import datetime
import unittest

import mock
import pytz

from greenpithumb import pump_history


class TestPumpHistory(unittest.TestCase):

    def setUp(self):
        self.mock_watering_event_store = mock.Mock()

    def test_last_pump_time_returns_None_when_db_is_empty(self):
        self.mock_watering_event_store.get.return_value = []
        self.assertEqual(
            None, pump_history.last_pump_time(self.mock_watering_event_store))

    def test_last_pump_time_returns_timestamp_when_only_one_event_in_db(self):
        self.mock_watering_event_store.get.return_value = [
            mock.Mock(timestamp=datetime.datetime(
                2017, 1, 1, 12, 45, 9, 123456, tzinfo=pytz.utc))
        ]
        self.assertEqual(
            datetime.datetime(2017, 1, 1, 12, 45, 9, 123456, tzinfo=pytz.utc),
            pump_history.last_pump_time(self.mock_watering_event_store))

    def test_last_pump_time_returns_timestamp_when_db_has_many_events(self):
        self.mock_watering_event_store.get.return_value = [
            mock.Mock(timestamp=datetime.datetime(
                2016, 1, 1, 12, 45, 9, 123456, tzinfo=pytz.utc)),
            mock.Mock(timestamp=datetime.datetime(
                2017, 3, 2, 0, 15, 59, 987654, tzinfo=pytz.utc)),
            mock.Mock(timestamp=datetime.datetime(
                2015, 12, 5, 12, 45, 9, 555555, tzinfo=pytz.utc)),
        ]
        self.assertEqual(
            datetime.datetime(2017, 3, 2, 0, 15, 59, 987654, tzinfo=pytz.utc),
            pump_history.last_pump_time(self.mock_watering_event_store))
