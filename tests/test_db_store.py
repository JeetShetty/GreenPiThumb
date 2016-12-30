import unittest

import mock
import datetime

from greenpithumb import db_store


class StoreClassesTest(unittest.TestCase):

    def test_store_soil_moisture(self):
        """Should insert timestamp and moisture level into database."""
        timestamp = datetime.datetime(2016, 7, 23, 10, 51, 9, 928000)
        soil_moisture = 300
        mock_cursor = mock.Mock()
        store = db_store.SoilMoistureStore(mock_cursor)
        store.store_soil_moisture(timestamp, soil_moisture)
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO soil_moisture VALUES (?, ?)", (timestamp,
                                                        soil_moisture))

    def test_latest_soil_moisture(self):
        mock_cursor = mock.Mock()
        store = db_store.SoilMoistureStore(mock_cursor)
        mock_cursor.fetchall.return_value = [(300,)]
        moisture = store.latest_soil_moisture()
        self.assertEqual(300, moisture)

    def test_latest_soil_moisture_empty_database(self):
        mock_cursor = mock.Mock()
        store = db_store.SoilMoistureStore(mock_cursor)
        mock_cursor.fetchall.return_value = []
        moisture = store.latest_soil_moisture()
        self.assertIsNone(moisture)

    def test_store_ambient_light(self):
        """Should insert timestamp and ambient light into database."""
        timestamp = datetime.datetime(2016, 7, 23, 10, 51, 9, 928000)
        ambient_light = 50.0
        mock_cursor = mock.Mock()
        store = db_store.AmbientLightStore(mock_cursor)
        store.store_ambient_light(timestamp, ambient_light)
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO ambient_light VALUES (?, ?)", (timestamp,
                                                        ambient_light))

    def test_store_humidity(self):
        """Should insert timestamp and humidity level into database."""
        timestamp = datetime.datetime(2016, 7, 23, 10, 51, 9, 928000)
        humidity = 50.0
        mock_cursor = mock.Mock()
        store = db_store.HumidityStore(mock_cursor)
        store.store_humidity(timestamp, humidity)
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO ambient_humidity VALUES (?, ?)", (timestamp, humidity))

    def test_store_reservoir_level(self):
        """Should insert timestamp and reservoir level into detabase."""
        timestamp = datetime.datetime(2016, 7, 23, 10, 51, 9, 928000)
        reservoir_level = 1000.0
        mock_cursor = mock.Mock()
        store = db_store.ReservoirLevelStore(mock_cursor)
        store.store_reservoir_level(timestamp, reservoir_level)
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO reservoir_level VALUES (?, ?)", (timestamp,
                                                          reservoir_level))

    def test_store_temperature(self):
        """Should insert timestamp and temperature into database."""
        timestamp = datetime.datetime(2016, 7, 23, 10, 51, 9, 928000)
        temperature = 21.1
        mock_cursor = mock.Mock()
        store = db_store.TemperatureStore(mock_cursor)
        store.store_temperature(timestamp, temperature)
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO temperature VALUES (?, ?)", (timestamp, temperature))

    def test_store_water_pumped(self):
        """Should insert timestamp and volume of water pumped into database."""
        timestamp = datetime.datetime(2016, 7, 23, 10, 51, 9, 928000)
        water_pumped = 200.0
        mock_cursor = mock.Mock()
        store = db_store.WateringEventStore(mock_cursor)
        store.store_water_pumped(timestamp, water_pumped)
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO watering_events VALUES (?, ?)", (timestamp,
                                                          water_pumped))
