from __future__ import absolute_import
import unittest

import mock
import datetime

from greenpithumb import temperature_store


class TemperatureStoreTest(unittest.TestCase):

    def test_store_temperature_inserts_timestamp_temperature(self):
        timestamp = datetime.datetime(2016, 7, 23, 10, 51, 9, 928000)
        temperature = 21.1
        mock_cursor = mock.Mock()
        store = temperature_store.TemperatureStore(mock_cursor)
        store.store_temperature(timestamp, temperature)
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO temperature VALUES (?, ?)", (timestamp, temperature))
