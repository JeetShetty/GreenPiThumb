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
# TIMESTAMP_B is on the poll interval boundary immediately after TIMESTAMP_A.
TIMESTAMP_B = datetime.datetime(2016, 7, 23, 10, 51, 15, 0, tzinfo=pytz.utc)


class PollerTest(unittest.TestCase):

    def setUp(self):
        self.clock_wait_event = threading.Event()
        self.mock_clock = mock.Mock()
        self.mock_clock.wait.side_effect = (
            lambda _: self.clock_wait_event.set())
        self.mock_sensor = mock.Mock()
        self.mock_store = mock.Mock()
        poll_interval = datetime.timedelta(seconds=15)
        self.record_queue = Queue.Queue()
        self.factory = poller.SensorPollerFactory(
            self.mock_clock, poll_interval, self.record_queue)

    def block_until_clock_wait_call(self):
        """Blocks until the clock's wait method is called or test times out."""
        self.clock_wait_event.wait(TEST_TIMEOUT_SECONDS)
        self.clock_wait_event.clear()


class SimplePollerClassesTest(PollerTest):

    def test_temperature_poller(self):
        with contextlib.closing(
                self.factory.create_temperature_poller(
                    self.mock_sensor)) as temperature_poller:
            self.mock_clock.now.return_value = TIMESTAMP_A
            self.mock_sensor.temperature.return_value = 21.0

            temperature_poller.start_polling_async()
            self.block_until_clock_wait_call()
            self.mock_clock.now.return_value = TIMESTAMP_B
            self.block_until_clock_wait_call()

        self.assertEqual(
            db_store.TemperatureRecord(
                timestamp=TIMESTAMP_B, temperature=21.0),
            self.record_queue.get(block=True, timeout=TEST_TIMEOUT_SECONDS))
        # Should be no more items in the queue.
        self.assertTrue(self.record_queue.empty())

    def test_humidity_poller(self):
        with contextlib.closing(
                self.factory.create_humidity_poller(
                    self.mock_sensor)) as humidity_poller:
            self.mock_clock.now.return_value = TIMESTAMP_A
            self.mock_sensor.humidity.return_value = 50.0

            humidity_poller.start_polling_async()
            self.block_until_clock_wait_call()
            self.mock_clock.now.return_value = TIMESTAMP_B
            self.block_until_clock_wait_call()

        self.assertEqual(
            db_store.HumidityRecord(
                timestamp=TIMESTAMP_B, humidity=50.0),
            self.record_queue.get(block=True, timeout=TEST_TIMEOUT_SECONDS))
        # Should be no more items in the queue.
        self.assertTrue(self.record_queue.empty())

    def test_light_poller(self):
        with contextlib.closing(
                self.factory.create_light_poller(
                    self.mock_sensor)) as light_poller:
            self.mock_clock.now.return_value = TIMESTAMP_A
            self.mock_sensor.light.return_value = 50.0

            light_poller.start_polling_async()
            self.block_until_clock_wait_call()
            self.mock_clock.now.return_value = TIMESTAMP_B
            self.block_until_clock_wait_call()

        self.assertEqual(
            db_store.LightRecord(
                timestamp=TIMESTAMP_B, light=50.0),
            self.record_queue.get(block=True, timeout=TEST_TIMEOUT_SECONDS))
        # Should be no more items in the queue.
        self.assertTrue(self.record_queue.empty())


class SoilWateringPollerTest(PollerTest):

    def setUp(self):
        super(SoilWateringPollerTest, self).setUp()
        self.mock_pump_manager = mock.Mock()
        self.mock_soil_moisture_sensor = mock.Mock()

    def test_soil_watering_poller_when_pump_run(self):
        with contextlib.closing(
                self.factory.create_soil_watering_poller(
                    self.mock_soil_moisture_sensor,
                    self.mock_pump_manager)) as soil_watering_poller:
            self.mock_clock.now.return_value = TIMESTAMP_A
            self.mock_pump_manager.pump_if_needed.return_value = 200
            self.mock_soil_moisture_sensor.soil_moisture.return_value = 100

            soil_watering_poller.start_polling_async()
            self.block_until_clock_wait_call()
            self.mock_clock.now.return_value = TIMESTAMP_B
            self.block_until_clock_wait_call()

        records_expected = [
            db_store.SoilMoistureRecord(
                timestamp=TIMESTAMP_B, soil_moisture=100),
            db_store.WateringEventRecord(
                timestamp=TIMESTAMP_B, water_pumped=200.0)
        ]
        records_actual = [
            self.record_queue.get(block=True, timeout=TEST_TIMEOUT_SECONDS),
            self.record_queue.get(block=True, timeout=TEST_TIMEOUT_SECONDS)
        ]
        self.assertItemsEqual(records_expected, records_actual)
        # Should be no more items in the queue.
        self.assertTrue(self.record_queue.empty())
        self.mock_pump_manager.pump_if_needed.assert_called_with(100)

    def test_soil_watering_poller_when_pump_not_run(self):
        with contextlib.closing(
                self.factory.create_soil_watering_poller(
                    self.mock_soil_moisture_sensor,
                    self.mock_pump_manager)) as soil_watering_poller:
            self.mock_clock.now.return_value = TIMESTAMP_A
            self.mock_pump_manager.pump_if_needed.return_value = 0
            self.mock_soil_moisture_sensor.soil_moisture.return_value = 500

            soil_watering_poller.start_polling_async()
            self.block_until_clock_wait_call()
            self.mock_clock.now.return_value = TIMESTAMP_B
            self.block_until_clock_wait_call()

        self.assertEqual(
            db_store.SoilMoistureRecord(
                timestamp=TIMESTAMP_B, soil_moisture=500),
            self.record_queue.get(block=True, timeout=TEST_TIMEOUT_SECONDS))
        # Should be no more items in the queue.
        self.assertTrue(self.record_queue.empty())
        self.mock_pump_manager.pump_if_needed.assert_called_with(500)


class CameraPollerTest(PollerTest):

    def setUp(self):
        super(CameraPollerTest, self).setUp()
        self.mock_camera_manager = mock.Mock()

    def test_camera_poller(self):
        with contextlib.closing(
                self.factory.create_camera_poller(
                    self.mock_camera_manager)) as camera_poller:
            self.mock_clock.now.return_value = TIMESTAMP_A

            camera_poller.start_polling_async()
            self.block_until_clock_wait_call()
            self.mock_clock.now.return_value = TIMESTAMP_B
            self.block_until_clock_wait_call()

        self.mock_camera_manager.save_photo.assert_called()
        self.mock_camera_manager.close.assert_called()
        # Should be nothing items in the queue because CameraPoller does not
        # create database records.
        self.assertTrue(self.record_queue.empty())
