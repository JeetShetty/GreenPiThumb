import contextlib
import datetime
import Queue
import threading
import unittest

import mock
import pytz

from greenpithumb import db_store
from greenpithumb import poller

TEST_TIMEOUT_SECONDS = 3.0
TIMESTAMP_A = datetime.datetime(2016, 7, 23, 10, 51, 9, 928000, tzinfo=pytz.utc)
POLL_INTERVAL = 1


class PollerClassesTest(unittest.TestCase):

    def setUp(self):
        self.clock_wait_event = threading.Event()
        self.mock_local_clock = mock.Mock()
        self.mock_sensor = mock.Mock()
        self.mock_store = mock.Mock()
        self.record_queue = Queue.Queue()

    def test_temperature_poller(self):
        with contextlib.closing(
                poller.TemperaturePoller(
                    self.mock_local_clock, POLL_INTERVAL, self.mock_sensor,
                    self.record_queue)) as temperature_poller:
            self.mock_local_clock.now.return_value = TIMESTAMP_A
            self.mock_local_clock.wait.side_effect = (
                lambda _: self.clock_wait_event.set())
            self.mock_sensor.temperature.return_value = 21.0

            temperature_poller.start_polling_async()
            self.clock_wait_event.wait(TEST_TIMEOUT_SECONDS)

        self.assertEqual(
            db_store.TemperatureRecord(
                timestamp=TIMESTAMP_A, temperature=21.0),
            self.record_queue.get(block=True, timeout=TEST_TIMEOUT_SECONDS))
        self.mock_local_clock.wait.assert_called_with(POLL_INTERVAL)

    def test_humidity_poller(self):
        with contextlib.closing(
                poller.HumidityPoller(self.mock_local_clock, POLL_INTERVAL,
                                      self.mock_sensor,
                                      self.record_queue)) as humidity_poller:
            self.mock_local_clock.now.return_value = TIMESTAMP_A
            self.mock_local_clock.wait.side_effect = (
                lambda _: self.clock_wait_event.set())
            self.mock_sensor.humidity.return_value = 50.0

            humidity_poller.start_polling_async()
            self.clock_wait_event.wait(TEST_TIMEOUT_SECONDS)

        self.assertEqual(
            db_store.HumidityRecord(
                timestamp=TIMESTAMP_A, humidity=50.0),
            self.record_queue.get(block=True, timeout=TEST_TIMEOUT_SECONDS))
        self.mock_local_clock.wait.assert_called_with(POLL_INTERVAL)

    def test_ambient_light_poller(self):
        with contextlib.closing(
                poller.AmbientLightPoller(
                    self.mock_local_clock, POLL_INTERVAL, self.mock_sensor,
                    self.record_queue)) as ambient_light_poller:
            self.mock_local_clock.now.return_value = TIMESTAMP_A
            self.mock_local_clock.wait.side_effect = (
                lambda _: self.clock_wait_event.set())
            self.mock_sensor.ambient_light.return_value = 50.0

            ambient_light_poller.start_polling_async()
            self.clock_wait_event.wait(TEST_TIMEOUT_SECONDS)

        self.assertEqual(
            db_store.AmbientLightRecord(
                timestamp=TIMESTAMP_A, ambient_light=50.0),
            self.record_queue.get(block=True, timeout=TEST_TIMEOUT_SECONDS))
        self.mock_local_clock.wait.assert_called_with(POLL_INTERVAL)


class SoilWateringPollerTest(unittest.TestCase):

    def setUp(self):
        self.clock_wait_event = threading.Event()
        self.mock_local_clock = mock.Mock()
        self.mock_pump_manager = mock.Mock()
        self.mock_soil_moisture_sensor = mock.Mock()
        self.record_queue = Queue.Queue()

    def _stop_poller(self, poller):
        poller.close()
        self.clock_wait_event.set()

    def test_soil_watering_poller_when_pump_run(self):
        with contextlib.closing(
                poller.SoilWateringPoller(
                    self.mock_local_clock, POLL_INTERVAL,
                    self.mock_soil_moisture_sensor, self.mock_pump_manager,
                    self.record_queue)) as soil_watering_poller:
            self.mock_local_clock.now.return_value = TIMESTAMP_A
            self.mock_local_clock.wait.side_effect = (
                lambda _: self._stop_poller(soil_watering_poller))
            self.mock_pump_manager.pump_if_needed.return_value = 200
            self.mock_soil_moisture_sensor.moisture.return_value = 100

            soil_watering_poller.start_polling_async()
            self.clock_wait_event.wait(TEST_TIMEOUT_SECONDS)
        records_expected = [
            db_store.SoilMoistureRecord(
                timestamp=TIMESTAMP_A, soil_moisture=100),
            db_store.WateringEventRecord(
                timestamp=TIMESTAMP_A, water_pumped=200.0)
        ]
        records_actual = [
            self.record_queue.get(block=True, timeout=TEST_TIMEOUT_SECONDS),
            self.record_queue.get(block=True, timeout=TEST_TIMEOUT_SECONDS)
        ]
        # Should be no more items in the queue.
        self.assertTrue(self.record_queue.empty())
        self.assertItemsEqual(records_expected, records_actual)
        self.mock_local_clock.wait.assert_called_with(POLL_INTERVAL)
        self.mock_pump_manager.pump_if_needed.assert_called_with(100)

    def test_soil_watering_poller_when_pump_not_run(self):
        with contextlib.closing(
                poller.SoilWateringPoller(
                    self.mock_local_clock, POLL_INTERVAL,
                    self.mock_soil_moisture_sensor, self.mock_pump_manager,
                    self.record_queue)) as soil_watering_poller:
            self.mock_local_clock.now.return_value = TIMESTAMP_A
            self.mock_local_clock.wait.side_effect = (
                lambda _: self._stop_poller(soil_watering_poller))
            self.mock_pump_manager.pump_if_needed.return_value = 0
            self.mock_soil_moisture_sensor.moisture.return_value = 500

            soil_watering_poller.start_polling_async()
            self.clock_wait_event.wait(TEST_TIMEOUT_SECONDS)
        self.assertEqual(
            db_store.SoilMoistureRecord(
                timestamp=TIMESTAMP_A, soil_moisture=500),
            self.record_queue.get(block=True, timeout=TEST_TIMEOUT_SECONDS))
        # Should be no more items in the queue.
        self.assertTrue(self.record_queue.empty())
        self.mock_local_clock.wait.assert_called_with(POLL_INTERVAL)
        self.mock_pump_manager.pump_if_needed.assert_called_with(500)


class CameraPollerTest(unittest.TestCase):

    def test_camera_poller(self):
        clock_wait_event = threading.Event()
        mock_local_clock = mock.Mock()
        mock_camera_manager = mock.Mock()
        with contextlib.closing(
                poller.CameraPoller(mock_local_clock, POLL_INTERVAL,
                                    mock_camera_manager)) as camera_poller:
            mock_local_clock.wait.side_effect = lambda _: clock_wait_event.set()

            camera_poller.start_polling_async()
            clock_wait_event.wait(TEST_TIMEOUT_SECONDS)
            mock_camera_manager.save_photo.assert_called()
