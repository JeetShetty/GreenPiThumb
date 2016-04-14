from __future__ import absolute_import
import unittest

import mock

from greenpithumb import pump_manager


class PumpManagerTest(unittest.TestCase):

    def setUp(self):
        self.mock_moisture_sensor = mock.Mock()
        self.mock_pump = mock.Mock()
        self.manager = pump_manager.PumpManager(
            self.mock_moisture_sensor,
            self.mock_pump)

    def test_low_moisture_triggers_pump(self):
        self.mock_moisture_sensor.moisture.return_value = (
            pump_manager.SOIL_MOISTURE_THRESHOLD - 100)
        self.manager.pump_if_needed()
        self.mock_pump.pump_water.assert_called_once_with(
            pump_manager.DEFAULT_PUMP_AMOUNT)

    def test_pump_not_triggered_if_moisture_is_at_threshold(self):
        self.mock_moisture_sensor.moisture.return_value = (
            pump_manager.SOIL_MOISTURE_THRESHOLD)
        self.manager.pump_if_needed()
        # Pump should not run if soil moisture is exactly at threshold.
        self.assertFalse(self.mock_pump.pump_water.called)

    def test_pump_not_triggered_if_moisture_is_high(self):
        self.mock_moisture_sensor.moisture.return_value = (
            pump_manager.SOIL_MOISTURE_THRESHOLD + 350)
        self.manager.pump_if_needed()
        # Pump should not run if soil moisture is above threshold.
        self.assertFalse(self.mock_pump.pump_water.called)

    def test_pump_is_disabled_during_quiet_hours(self):
        # TODO: Implement this.
        # We need to figure out a way of making the pump wait to pump until it's
        # non-sleep hours.
        pass
