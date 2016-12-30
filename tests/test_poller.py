import unittest

import mock
import datetime
import threading

from greenpithumb import poller

TEST_TIMEOUT_SECONDS = 3.0
TIMESTAMP_A = datetime.datetime(2016, 7, 23, 10, 51, 9, 928000)
POLL_INTERVAL = 1


class PollerClassesTest(unittest.TestCase):

    def setUp(self):
        self.clock_wait_event = threading.Event()
        self.mock_local_clock = mock.Mock()
        self.mock_sensor = mock.Mock()
        self.mock_store = mock.Mock()

    def test_temperature_poller(self):
        temperature_poller = poller.TemperaturePoller(
            self.mock_local_clock, POLL_INTERVAL, self.mock_sensor,
            self.mock_store)
        self.mock_local_clock.now.return_value = TIMESTAMP_A
        self.mock_local_clock.wait.side_effect = (
            lambda _: self.clock_wait_event.set())
        self.mock_sensor.temperature.return_value = 21.0

        temperature_poller.start_polling_async()
        self.clock_wait_event.wait(TEST_TIMEOUT_SECONDS)
        self.mock_store.store_temperature.assert_called_with(TIMESTAMP_A, 21.0)
        self.mock_local_clock.wait.assert_called_with(POLL_INTERVAL)

    def test_humidity_poller(self):
        humidity_poller = poller.HumidityPoller(self.mock_local_clock,
                                                POLL_INTERVAL, self.mock_sensor,
                                                self.mock_store)
        self.mock_local_clock.now.return_value = TIMESTAMP_A
        self.mock_local_clock.wait.side_effect = (
            lambda _: self.clock_wait_event.set())
        self.mock_sensor.humidity.return_value = 50.0

        humidity_poller.start_polling_async()
        self.clock_wait_event.wait(TEST_TIMEOUT_SECONDS)
        self.mock_store.store_humidity.assert_called_with(TIMESTAMP_A, 50.0)
        self.mock_local_clock.wait.assert_called_with(POLL_INTERVAL)

    def test_moisture_poller(self):
        moisture_poller = poller.MoisturePoller(self.mock_local_clock,
                                                POLL_INTERVAL, self.mock_sensor,
                                                self.mock_store)
        self.mock_local_clock.now.return_value = TIMESTAMP_A
        self.mock_local_clock.wait.side_effect = (
            lambda _: self.clock_wait_event.set())
        self.mock_sensor.moisture.return_value = 300

        moisture_poller.start_polling_async()
        self.clock_wait_event.wait(TEST_TIMEOUT_SECONDS)
        self.mock_store.store_soil_moisture.assert_called_with(TIMESTAMP_A, 300)
        self.mock_local_clock.wait.assert_called_with(POLL_INTERVAL)

    def test_ambient_light_poller(self):
        ambient_light_poller = poller.AmbientLightPoller(
            self.mock_local_clock, POLL_INTERVAL, self.mock_sensor,
            self.mock_store)
        self.mock_local_clock.now.return_value = TIMESTAMP_A
        self.mock_local_clock.wait.side_effect = (
            lambda _: self.clock_wait_event.set())
        self.mock_sensor.ambient_light.return_value = 50.0

        ambient_light_poller.start_polling_async()
        self.clock_wait_event.wait(TEST_TIMEOUT_SECONDS)
        self.mock_store.store_ambient_light.assert_called_with(TIMESTAMP_A,
                                                               50.0)
        self.mock_local_clock.wait.assert_called_with(POLL_INTERVAL)

    def test_reservoir_poller(self):
        reservoir_poller = poller.ReservoirPoller(
            self.mock_local_clock, POLL_INTERVAL, self.mock_sensor,
            self.mock_store)
        self.mock_local_clock.now.return_value = TIMESTAMP_A
        self.mock_local_clock.wait.side_effect = (
            lambda _: self.clock_wait_event.set())
        self.mock_sensor.reservoir_level.return_value = 500.0

        reservoir_poller.start_polling_async()
        self.clock_wait_event.wait(TEST_TIMEOUT_SECONDS)
        self.mock_store.store_reservoir_level.assert_called_with(TIMESTAMP_A,
                                                                 500.0)
        self.mock_local_clock.wait.assert_called_with(POLL_INTERVAL)


class WateringEventPollerTest(unittest.TestCase):

    def setUp(self):
        self.clock_wait_event = threading.Event()
        self.mock_local_clock = mock.Mock()
        self.mock_pump_manager = mock.Mock()
        self.mock_watering_event_store = mock.Mock()
        self.mock_soil_moisture_store = mock.Mock()

    def test_watering_event_poller_when_pump_run(self):
        watering_event_poller = poller.WateringEventPoller(
            self.mock_local_clock, POLL_INTERVAL, self.mock_pump_manager,
            self.mock_watering_event_store, self.mock_soil_moisture_store)
        self.mock_local_clock.now.return_value = TIMESTAMP_A
        self.mock_local_clock.wait.side_effect = (
            lambda _: self.clock_wait_event.set())
        self.mock_pump_manager.pump_if_needed.return_value = 200
        self.mock_soil_moisture_store.latest_soil_moisture.return_value = 100

        watering_event_poller.start_polling_async()
        self.clock_wait_event.wait(TEST_TIMEOUT_SECONDS)
        self.mock_watering_event_store.store_water_pumped.assert_called_with(
            TIMESTAMP_A, 200)
        self.mock_local_clock.wait.assert_called_with(POLL_INTERVAL)
        self.mock_pump_manager.pump_if_needed.assert_called_with(100)

    def test_watering_event_poller_when_pump_not_run(self):
        watering_event_poller = poller.WateringEventPoller(
            self.mock_local_clock, POLL_INTERVAL, self.mock_pump_manager,
            self.mock_watering_event_store, self.mock_soil_moisture_store)
        self.mock_local_clock.wait.side_effect = (
            lambda _: self.clock_wait_event.set())
        self.mock_pump_manager.pump_if_needed.return_value = 0
        self.mock_soil_moisture_store.latest_soil_moisture.return_value = 500

        watering_event_poller.start_polling_async()
        self.clock_wait_event.wait(TEST_TIMEOUT_SECONDS)
        self.assertFalse(
            self.mock_watering_event_store.store_water_pumped.called)
        self.mock_local_clock.wait.assert_called_with(POLL_INTERVAL)
        self.mock_pump_manager.pump_if_needed.assert_called_with(500)

    def test_watering_event_poller_when_moisture_is_None(self):
        watering_event_poller = poller.WateringEventPoller(
            self.mock_local_clock, POLL_INTERVAL, self.mock_pump_manager,
            self.mock_watering_event_store, self.mock_soil_moisture_store)
        self.mock_local_clock.wait.side_effect = (
            lambda _: self.clock_wait_event.set())
        self.mock_soil_moisture_store.latest_soil_moisture.return_value = None

        watering_event_poller.start_polling_async()
        self.clock_wait_event.wait(TEST_TIMEOUT_SECONDS)
        self.assertFalse(
            self.mock_watering_event_store.store_water_pumped.called)
        self.assertFalse(self.mock_pump_manager.pump_if_needed.called)
        self.mock_local_clock.wait.assert_called_with(POLL_INTERVAL)
