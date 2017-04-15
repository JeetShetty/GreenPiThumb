import contextlib
import datetime
import Queue
import threading
import unittest

import mock
import pytz

from greenpithumb import db_store
from greenpithumb import poller

TEST_TIMEOUT_SECONDS = 0.5
TIMESTAMP_A = datetime.datetime(2016, 7, 23, 10, 51, 9, 928000, tzinfo=pytz.utc)


class SchedulerTest(unittest.TestCase):

    def setUp(self):
        self.mock_clock = mock.Mock()

    def test_wait_less_than_timeout_returns_True(self):
        self.mock_clock.now.return_value = datetime.datetime(
            2017, 4, 9, 11, 43, 29, tzinfo=pytz.utc)
        scheduler = poller.Scheduler(
            self.mock_clock, poll_interval=datetime.timedelta(minutes=5))
        self.assertTrue(scheduler.wait_until_poll_time(timeout=(10 * 60)))
        # If it's 11:43:29, at 5m polling intervals, next poll is at 11:45:00,
        # 91 seconds later.
        self.mock_clock.wait.assert_called_with(91)

    def test_wait_more_than_timeout_returns_False(self):
        self.mock_clock.now.return_value = datetime.datetime(
            2017, 4, 9, 11, 43, 29, tzinfo=pytz.utc)
        scheduler = poller.Scheduler(
            self.mock_clock, poll_interval=datetime.timedelta(minutes=5))
        # If it's 11:43:29, at 5m polling intervals, next poll is at 11:45:00,
        # 91 seconds later, so we should only wait the length of the timeout.
        self.assertFalse(scheduler.wait_until_poll_time(timeout=90))
        self.mock_clock.wait.assert_called_with(90)

    def test_wait_equal_to_timeout_returns_True(self):
        self.mock_clock.now.return_value = datetime.datetime(
            2017, 4, 9, 11, 43, 29, tzinfo=pytz.utc)
        scheduler = poller.Scheduler(
            self.mock_clock, poll_interval=datetime.timedelta(minutes=5))
        # If it's 11:43:29, at 5m polling intervals, next poll is at 11:45:00,
        # 91 seconds later, so timeout is equal to wait time.
        self.assertTrue(scheduler.wait_until_poll_time(timeout=91))
        self.mock_clock.wait.assert_called_with(91)

    def test_no_wait_if_first_call_is_on_interval_boundary(self):
        self.mock_clock.now.return_value = datetime.datetime(
            2017, 4, 9, 11, 45, 0, tzinfo=pytz.utc)
        scheduler = poller.Scheduler(
            self.mock_clock, poll_interval=datetime.timedelta(minutes=5))
        self.assertTrue(scheduler.wait_until_poll_time(timeout=(10 * 60)))
        # 11:45:00 falls on the interval boundary of 5m, so should be no wait.
        self.mock_clock.wait.assert_not_called()

    def test_increments_wait_if_consecutive_calls_on_same_poll_boundary(self):
        self.mock_clock.now.return_value = datetime.datetime(
            2017, 4, 9, 11, 45, 0, tzinfo=pytz.utc)
        scheduler = poller.Scheduler(
            self.mock_clock, poll_interval=datetime.timedelta(minutes=5))
        self.assertTrue(scheduler.wait_until_poll_time(timeout=(10 * 60)))
        # First call should have no wait because it's on a poll interval
        # boundary.
        self.mock_clock.wait.assert_not_called()
        # On next call, we should wait until the *next* poll interval boundary.
        self.assertTrue(scheduler.wait_until_poll_time(timeout=(10 * 60)))
        self.mock_clock.wait.assert_called_with(5 * 60)

    def test_last_poll_time_is_None_before_wait_called(self):
        self.mock_clock.now.return_value = datetime.datetime(
            2017, 4, 9, 11, 43, 29, tzinfo=pytz.utc)
        scheduler = poller.Scheduler(
            self.mock_clock, poll_interval=datetime.timedelta(minutes=5))
        # If no poll has happened, last_poll_time should be None.
        self.assertIsNone(scheduler.last_poll_time())

    def test_last_poll_time_is_None_before_poll_wait_completes(self):
        self.mock_clock.now.return_value = datetime.datetime(
            2017, 4, 9, 11, 43, 29, tzinfo=pytz.utc)
        scheduler = poller.Scheduler(
            self.mock_clock, poll_interval=datetime.timedelta(minutes=5))

        # If we wait for poll, but timeout is not long enough for a poll to
        # happen, last_poll_time should not change.
        self.assertFalse(scheduler.wait_until_poll_time(timeout=30))
        self.assertIsNone(scheduler.last_poll_time())

    def test_last_poll_time_updates_when_wait_completes(self):
        self.mock_clock.now.return_value = datetime.datetime(
            2017, 4, 9, 11, 43, 29, tzinfo=pytz.utc)
        scheduler = poller.Scheduler(
            self.mock_clock, poll_interval=datetime.timedelta(minutes=5))

        # If a poll completes, last_poll_time should update to the last poll
        # time.
        self.assertTrue(scheduler.wait_until_poll_time(timeout=120))
        self.assertEqual(
            datetime.datetime(
                2017, 4, 9, 11, 45, 0, tzinfo=pytz.utc),
            scheduler.last_poll_time())

        self.mock_clock.now.return_value = datetime.datetime(
            2017, 4, 9, 11, 49, 29, tzinfo=pytz.utc)
        self.assertTrue(scheduler.wait_until_poll_time(timeout=120))
        self.assertEqual(
            datetime.datetime(
                2017, 4, 9, 11, 50, 0, tzinfo=pytz.utc),
            scheduler.last_poll_time())


class PollerTest(unittest.TestCase):

    def setUp(self):
        self.scheduler_wait_event = threading.Event()
        self.mock_scheduler = mock.Mock()
        self.mock_is_poll_time = False
        self.mock_scheduler.wait_until_poll_time.side_effect = (
            self.mock_wait_until_poll_time)
        make_scheduler_func = lambda: self.mock_scheduler
        self.mock_sensor = mock.Mock()
        self.mock_store = mock.Mock()
        self.record_queue = Queue.Queue()
        self.factory = poller.SensorPollerFactory(make_scheduler_func,
                                                  self.record_queue)

    def mock_wait_until_poll_time(self, _):
        wait_result = self.mock_is_poll_time
        self.mock_is_poll_time = False
        self.scheduler_wait_event.set()
        return wait_result

    def block_until_scheduler_wait_call(self):
        """Blocks until the clock's wait method is called or test times out."""
        self.scheduler_wait_event.wait(TEST_TIMEOUT_SECONDS)
        self.scheduler_wait_event.clear()

    def block_until_poll_completes(self):
        """Blocks until the poller has completed one poll event."""
        # Wait until call to schedule the first poll.
        self.block_until_scheduler_wait_call()
        # Wait until call to schedule the second poll, which indicates the first
        # poll is complete.
        self.block_until_scheduler_wait_call()


class SimplePollerClassesTest(PollerTest):

    def test_temperature_poller(self):
        with contextlib.closing(
                self.factory.create_temperature_poller(
                    self.mock_sensor)) as temperature_poller:
            self.mock_is_poll_time = True
            self.mock_scheduler.last_poll_time.return_value = TIMESTAMP_A
            self.mock_sensor.temperature.return_value = 21.0

            temperature_poller.start_polling_async()
            self.block_until_poll_completes()

        self.assertEqual(
            db_store.TemperatureRecord(
                timestamp=TIMESTAMP_A, temperature=21.0),
            self.record_queue.get(block=True, timeout=TEST_TIMEOUT_SECONDS))
        # Should be no more items in the queue.
        self.assertTrue(self.record_queue.empty())

    def test_humidity_poller(self):
        with contextlib.closing(
                self.factory.create_humidity_poller(
                    self.mock_sensor)) as humidity_poller:
            self.mock_is_poll_time = True
            self.mock_scheduler.last_poll_time.return_value = TIMESTAMP_A
            self.mock_sensor.humidity.return_value = 50.0

            humidity_poller.start_polling_async()
            self.block_until_poll_completes()

        self.assertEqual(
            db_store.HumidityRecord(
                timestamp=TIMESTAMP_A, humidity=50.0),
            self.record_queue.get(block=True, timeout=TEST_TIMEOUT_SECONDS))
        # Should be no more items in the queue.
        self.assertTrue(self.record_queue.empty())

    def test_light_poller(self):
        with contextlib.closing(
                self.factory.create_light_poller(
                    self.mock_sensor)) as light_poller:
            self.mock_is_poll_time = True
            self.mock_scheduler.last_poll_time.return_value = TIMESTAMP_A
            self.mock_sensor.light.return_value = 50.0

            light_poller.start_polling_async()
            self.block_until_poll_completes()

        self.assertEqual(
            db_store.LightRecord(
                timestamp=TIMESTAMP_A, light=50.0),
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
            self.mock_is_poll_time = True
            self.mock_scheduler.last_poll_time.return_value = TIMESTAMP_A
            self.mock_pump_manager.pump_if_needed.return_value = 200
            self.mock_soil_moisture_sensor.soil_moisture.return_value = 100

            soil_watering_poller.start_polling_async()
            self.block_until_poll_completes()

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
        self.assertItemsEqual(records_expected, records_actual)
        # Should be no more items in the queue.
        self.assertTrue(self.record_queue.empty())
        self.mock_pump_manager.pump_if_needed.assert_called_with(100)

    def test_soil_watering_poller_when_pump_not_run(self):
        with contextlib.closing(
                self.factory.create_soil_watering_poller(
                    self.mock_soil_moisture_sensor,
                    self.mock_pump_manager)) as soil_watering_poller:
            self.mock_is_poll_time = True
            self.mock_scheduler.last_poll_time.return_value = TIMESTAMP_A
            self.mock_pump_manager.pump_if_needed.return_value = 0
            self.mock_soil_moisture_sensor.soil_moisture.return_value = 500

            soil_watering_poller.start_polling_async()
            self.block_until_poll_completes()

        self.assertEqual(
            db_store.SoilMoistureRecord(
                timestamp=TIMESTAMP_A, soil_moisture=500),
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
            self.mock_is_poll_time = True
            camera_poller.start_polling_async()
            self.block_until_poll_completes()

        self.mock_camera_manager.save_photo.assert_called()
        self.mock_camera_manager.close.assert_called()
        # Should be nothing items in the queue because CameraPoller does not
        # create database records.
        self.assertTrue(self.record_queue.empty())
