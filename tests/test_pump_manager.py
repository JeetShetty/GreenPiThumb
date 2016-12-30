import unittest

import mock

from greenpithumb import pump_manager


class PumpManagerTest(unittest.TestCase):

    def setUp(self):
        self.mock_pump = mock.Mock()
        self.mock_pump_scheduler = mock.Mock()
        self.manager = pump_manager.PumpManager(self.mock_pump,
                                                self.mock_pump_scheduler)

    def test_low_moisture_triggers_pump(self):
        self.mock_pump_scheduler.is_running_pump_allowed.return_value = True
        moisture = pump_manager.SOIL_MOISTURE_THRESHOLD - 100
        ml_pumped = self.manager.pump_if_needed(moisture)
        self.mock_pump.pump_water.assert_called_once_with(
            pump_manager.DEFAULT_PUMP_AMOUNT)
        self.assertEqual(ml_pumped, pump_manager.DEFAULT_PUMP_AMOUNT)

    def test_pump_not_triggered_if_moisture_is_at_threshold(self):
        self.mock_pump_scheduler.is_running_pump_allowed.return_value = True
        moisture = pump_manager.SOIL_MOISTURE_THRESHOLD
        ml_pumped = self.manager.pump_if_needed(moisture)
        # Pump should not run if soil moisture is exactly at threshold.
        self.assertFalse(self.mock_pump.pump_water.called)
        self.assertEqual(ml_pumped, 0)

    def test_pump_not_triggered_if_moisture_is_high(self):
        self.mock_pump_scheduler.is_running_pump_allowed.return_value = True
        moisture = pump_manager.SOIL_MOISTURE_THRESHOLD + 350
        ml_pumped = self.manager.pump_if_needed(moisture)
        # Pump should not run if soil moisture is above threshold.
        self.assertFalse(self.mock_pump.pump_water.called)
        self.assertEqual(ml_pumped, 0)

    def test_pump_is_disabled_during_quiet_hours(self):
        self.mock_pump_scheduler.is_running_pump_allowed.return_value = False
        moisture = pump_manager.SOIL_MOISTURE_THRESHOLD - 100
        ml_pumped = self.manager.pump_if_needed(moisture)
        self.assertFalse(self.mock_pump.pump_water.called)
        self.assertEqual(ml_pumped, 0)
