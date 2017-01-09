import unittest
import datetime

import mock
from dateutil import tz
import pytz

from greenpithumb import db_store

# Timezone offset info for EST (UTC minus 5 hours).
UTC_MINUS_5 = tz.tzoffset(None, -18000)


class StoreClassesTest(unittest.TestCase):

    def test_store_soil_moisture(self):
        """Should insert timestamp and moisture level into database."""
        timestamp = datetime.datetime(
            2016, 7, 23, 10, 51, 9, 928000, tzinfo=pytz.utc)
        soil_moisture = 300
        mock_cursor = mock.Mock()
        store = db_store.SoilMoistureStore(mock_cursor)
        store.store_soil_moisture(timestamp, soil_moisture)
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO soil_moisture VALUES (?, ?)", (
                '2016-07-23T10:51:09.928000+00:00', soil_moisture))

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

    def test_retrieve_soil_moisture(self):
        mock_cursor = mock.Mock()
        store = db_store.SoilMoistureStore(mock_cursor)
        mock_cursor.fetchall.return_value = [
            ('2016-07-23 10:51:09.928000-05:00', 300),
            ('2016-07-23 10:52:09.928000-05:00', 400)
        ]
        soil_moisture_data = store.retrieve_soil_moisture()
        soil_moisture_data.sort(
            key=lambda SoilMoistureRecord: SoilMoistureRecord.timestamp)

        self.assertEqual(
            soil_moisture_data[0].timestamp,
            datetime.datetime(
                2016, 7, 23, 10, 51, 9, 928000, tzinfo=UTC_MINUS_5))
        self.assertEqual(soil_moisture_data[0].soil_moisture, 300)
        self.assertEqual(
            soil_moisture_data[1].timestamp,
            datetime.datetime(
                2016, 7, 23, 10, 52, 9, 928000, tzinfo=UTC_MINUS_5))
        self.assertEqual(soil_moisture_data[1].soil_moisture, 400)

    def test_retrieve_soil_moisture_empty_database(self):
        mock_cursor = mock.Mock()
        store = db_store.SoilMoistureStore(mock_cursor)
        mock_cursor.fetchall.return_value = []
        soil_moisture_data = store.retrieve_soil_moisture()
        self.assertEqual(soil_moisture_data, [])

    def test_store_ambient_light(self):
        """Should insert timestamp and ambient light into database."""
        timestamp = datetime.datetime(
            2016, 7, 23, 10, 51, 9, 928000, tzinfo=pytz.utc)
        ambient_light = 50.0
        mock_cursor = mock.Mock()
        store = db_store.AmbientLightStore(mock_cursor)
        store.store_ambient_light(timestamp, ambient_light)
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO ambient_light VALUES (?, ?)", (
                '2016-07-23T10:51:09.928000+00:00', ambient_light))

    def test_retrieve_ambient_light(self):
        mock_cursor = mock.Mock()
        store = db_store.AmbientLightStore(mock_cursor)
        mock_cursor.fetchall.return_value = [
            ('2016-07-23 10:51:09.928000-05:00', 300),
            ('2016-07-23 10:52:09.928000-05:00', 400)
        ]
        ambient_light_data = store.retrieve_ambient_light()
        ambient_light_data.sort(
            key=lambda AmbientLightRecord: AmbientLightRecord.timestamp)

        self.assertEqual(
            ambient_light_data[0].timestamp,
            datetime.datetime(
                2016, 7, 23, 10, 51, 9, 928000, tzinfo=UTC_MINUS_5))
        self.assertEqual(ambient_light_data[0].ambient_light, 300)
        self.assertEqual(
            ambient_light_data[1].timestamp,
            datetime.datetime(
                2016, 7, 23, 10, 52, 9, 928000, tzinfo=UTC_MINUS_5))
        self.assertEqual(ambient_light_data[1].ambient_light, 400)

    def test_retrieve_ambient_light_empty_database(self):
        mock_cursor = mock.Mock()
        store = db_store.AmbientLightStore(mock_cursor)
        mock_cursor.fetchall.return_value = []
        ambient_light_data = store.retrieve_ambient_light()
        self.assertEqual(ambient_light_data, [])

    def test_store_humidity(self):
        """Should insert timestamp and humidity level into database."""
        timestamp = datetime.datetime(
            2016, 7, 23, 10, 51, 9, 928000, tzinfo=pytz.utc)
        humidity = 50.0
        mock_cursor = mock.Mock()
        store = db_store.HumidityStore(mock_cursor)
        store.store_humidity(timestamp, humidity)
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO ambient_humidity VALUES (?, ?)",
            ('2016-07-23T10:51:09.928000+00:00', humidity))

    def test_retrieve_humidity(self):
        mock_cursor = mock.Mock()
        store = db_store.HumidityStore(mock_cursor)
        mock_cursor.fetchall.return_value = [
            ('2016-07-23 10:51:09.928000-05:00', 50),
            ('2016-07-23 10:52:09.928000-05:00', 51)
        ]
        humidity_data = store.retrieve_humidity()
        humidity_data.sort(key=lambda HumidityRecord: HumidityRecord.timestamp)

        self.assertEqual(
            humidity_data[0].timestamp,
            datetime.datetime(
                2016, 7, 23, 10, 51, 9, 928000, tzinfo=UTC_MINUS_5))
        self.assertEqual(humidity_data[0].humidity, 50)
        self.assertEqual(
            humidity_data[1].timestamp,
            datetime.datetime(
                2016, 7, 23, 10, 52, 9, 928000, tzinfo=UTC_MINUS_5))
        self.assertEqual(humidity_data[1].humidity, 51)

    def test_retrieve_humidity_empty_database(self):
        mock_cursor = mock.Mock()
        store = db_store.HumidityStore(mock_cursor)
        mock_cursor.fetchall.return_value = []
        humidity_data = store.retrieve_humidity()
        self.assertEqual(humidity_data, [])

    def test_store_reservoir_level(self):
        """Should insert timestamp and reservoir level into detabase."""
        timestamp = datetime.datetime(
            2016, 7, 23, 10, 51, 9, 928000, tzinfo=pytz.utc)
        reservoir_level = 1000.0
        mock_cursor = mock.Mock()
        store = db_store.ReservoirLevelStore(mock_cursor)
        store.store_reservoir_level(timestamp, reservoir_level)
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO reservoir_level VALUES (?, ?)", (
                '2016-07-23T10:51:09.928000+00:00', reservoir_level))

    def test_retrieve_reservoir_level(self):
        mock_cursor = mock.Mock()
        store = db_store.ReservoirLevelStore(mock_cursor)
        mock_cursor.fetchall.return_value = [
            ('2016-07-23 10:51:09.928000-05:00', 1000),
            ('2016-07-23 10:52:09.928000-05:00', 1200)
        ]
        reservoir_level_data = store.retrieve_reservoir_level()
        reservoir_level_data.sort(
            key=lambda ReservoirLevelRecord: ReservoirLevelRecord.timestamp)

        self.assertEqual(
            reservoir_level_data[0].timestamp,
            datetime.datetime(
                2016, 7, 23, 10, 51, 9, 928000, tzinfo=UTC_MINUS_5))
        self.assertEqual(reservoir_level_data[0].reservoir_level, 1000)
        self.assertEqual(
            reservoir_level_data[1].timestamp,
            datetime.datetime(
                2016, 7, 23, 10, 52, 9, 928000, tzinfo=UTC_MINUS_5))
        self.assertEqual(reservoir_level_data[1].reservoir_level, 1200)

    def test_retrieve_reservoir_level_empty_database(self):
        mock_cursor = mock.Mock()
        store = db_store.ReservoirLevelStore(mock_cursor)
        mock_cursor.fetchall.return_value = []
        reservoir_level_data = store.retrieve_reservoir_level()
        self.assertEqual(reservoir_level_data, [])

    def test_store_temperature(self):
        """Should insert timestamp and temperature into database."""
        timestamp = datetime.datetime(
            2016, 7, 23, 10, 51, 9, 928000, tzinfo=pytz.utc)
        temperature = 21.1
        mock_cursor = mock.Mock()
        store = db_store.TemperatureStore(mock_cursor)
        store.store_temperature(timestamp, temperature)
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO temperature VALUES (?, ?)",
            ('2016-07-23T10:51:09.928000+00:00', temperature))

    def test_retrieve_temperature(self):
        mock_cursor = mock.Mock()
        store = db_store.TemperatureStore(mock_cursor)
        mock_cursor.fetchall.return_value = [
            ('2016-07-23 10:51:09.928000-05:00', 21.0),
            ('2016-07-23 10:52:09.928000-05:00', 21.5)
        ]
        temperature_data = store.retrieve_temperature()
        temperature_data.sort(
            key=lambda TemperatureRecord: TemperatureRecord.timestamp)

        self.assertEqual(
            temperature_data[0].timestamp,
            datetime.datetime(
                2016, 7, 23, 10, 51, 9, 928000, tzinfo=UTC_MINUS_5))
        self.assertEqual(temperature_data[0].temperature, 21.0)
        self.assertEqual(
            temperature_data[1].timestamp,
            datetime.datetime(
                2016, 7, 23, 10, 52, 9, 928000, tzinfo=UTC_MINUS_5))
        self.assertEqual(temperature_data[1].temperature, 21.5)

    def test_retrieve_temperature_empty_database(self):
        mock_cursor = mock.Mock()
        store = db_store.TemperatureStore(mock_cursor)
        mock_cursor.fetchall.return_value = []
        temperature_data = store.retrieve_temperature()
        self.assertEqual(temperature_data, [])

    def test_store_water_pumped(self):
        """Should insert timestamp and volume of water pumped into database."""
        timestamp = datetime.datetime(
            2016, 7, 23, 10, 51, 9, 928000, tzinfo=pytz.utc)
        water_pumped = 200.0
        mock_cursor = mock.Mock()
        store = db_store.WateringEventStore(mock_cursor)
        store.store_water_pumped(timestamp, water_pumped)
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO watering_events VALUES (?, ?)", (
                '2016-07-23T10:51:09.928000+00:00', water_pumped))

    def test_retrieve_water_pumped(self):
        mock_cursor = mock.Mock()
        store = db_store.WateringEventStore(mock_cursor)
        mock_cursor.fetchall.return_value = [
            ('2016-07-23 10:51:09.928000-05:00', 300),
            ('2016-07-23 10:52:09.928000-05:00', 301)
        ]
        watering_event_data = store.retrieve_water_pumped()
        watering_event_data.sort(
            key=lambda WaterintEventRecord: WaterintEventRecord.timestamp)

        self.assertEqual(
            watering_event_data[0].timestamp,
            datetime.datetime(
                2016, 7, 23, 10, 51, 9, 928000, tzinfo=UTC_MINUS_5))
        self.assertEqual(watering_event_data[0].water_pumped, 300)
        self.assertEqual(
            watering_event_data[1].timestamp,
            datetime.datetime(
                2016, 7, 23, 10, 52, 9, 928000, tzinfo=UTC_MINUS_5))
        self.assertEqual(watering_event_data[1].water_pumped, 301)

    def test_retrieve_water_pumped_empty_database(self):
        mock_cursor = mock.Mock()
        store = db_store.WateringEventStore(mock_cursor)
        mock_cursor.fetchall.return_value = []
        watering_event_data = store.retrieve_water_pumped()
        self.assertEqual(watering_event_data, [])
