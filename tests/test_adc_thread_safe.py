import threading
import time
import unittest

import mock

from greenpithumb import adc_thread_safe


class AdcTest(unittest.TestCase):

    def setUp(self):
        self.counter = 0

    def increment_counter(self, amount):
        # Increment counter in a deliberately inefficient way to invite a race
        # condition if this is called by more than one thread at once.
        for i in range(amount):
            current = self.counter
            time.sleep(0.01)
            self.counter = current + 1

    def test_read_adc_is_thread_safe(self):
        raw_adc = mock.Mock()
        raw_adc.read_adc.side_effect = lambda x: self.increment_counter(10)
        adc = adc_thread_safe.Adc(raw_adc)
        threads = []
        # Spawn several threads to call read_adc concurrently to see if they
        # trigger a race condition.
        for _ in range(5):
            threads.append(threading.Thread(target=lambda: adc.read_adc(0)))
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        # Check that the threads incremented the counter correctly.
        self.assertEqual(10 * 5, self.counter)
