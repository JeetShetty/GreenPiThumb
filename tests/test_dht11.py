import unittest

import mock
import datetime

from greenpithumb import dht11


class CachingDHT11Test(unittest.TestCase):

    def setUp(self):
        self.mock_dht11_read_func = mock.Mock()
        self.mock_clock = mock.Mock()

    def test_gets_correct_readings_from_dht11(self):
        caching_dht11 = dht11.CachingDHT11(self.mock_dht11_read_func,
                                           self.mock_clock)
        self.mock_dht11_read_func.return_value = (50.0, 21.0)
        self.mock_clock.now.return_value = (
            datetime.datetime(2016, 1, 1, 0, 0, 0, 0))

        humidity = caching_dht11.humidity()
        temperature = caching_dht11.temperature()

        self.assertEqual(humidity, 50.0)
        self.assertEqual(temperature, 21.0)
        self.assertEqual(1, self.mock_dht11_read_func.call_count)

    def test_does_not_read_more_than_once_before_cache_expires(self):
        caching_dht11 = dht11.CachingDHT11(self.mock_dht11_read_func,
                                           self.mock_clock)
        self.mock_dht11_read_func.return_value = (50.0, 21.0)
        self.mock_clock.now.return_value = (
            datetime.datetime(2016, 1, 1, 0, 0, 0, 0))

        # Call humidity() and temperature() for the first time.
        caching_dht11.humidity()
        caching_dht11.temperature()
        self.assertEqual(1, self.mock_dht11_read_func.call_count)

        # Set clock to just below expiration time for cached values.
        self.mock_clock.now.return_value = (
            datetime.datetime(2016, 1, 1, 0, 0, 1, 999999))

        # Call humidity() and temperature() again to verify they don't cause a
        # second read.
        caching_dht11.humidity()
        caching_dht11.temperature()
        self.assertEqual(1, self.mock_dht11_read_func.call_count)

    def test_refreshes_cache_after_cached_values_expire(self):
        caching_dht11 = dht11.CachingDHT11(self.mock_dht11_read_func,
                                           self.mock_clock)
        self.mock_dht11_read_func.return_value = (50.0, 21.0)
        self.mock_clock.now.return_value = (
            datetime.datetime(2016, 1, 1, 0, 0, 0, 0))

        # Call humidity() and temperature() for the first time.
        caching_dht11.humidity()
        caching_dht11.temperature()
        self.assertEqual(1, self.mock_dht11_read_func.call_count)

        # Set clock to expiration time for cached values.
        self.mock_clock.now.return_value = (
            datetime.datetime(2016, 1, 1, 0, 0, 2, 0))

        # Call humidity() and temperature() again to verify they cause a second
        # read.
        caching_dht11.humidity()
        caching_dht11.temperature()
        self.assertEqual(2, self.mock_dht11_read_func.call_count)
