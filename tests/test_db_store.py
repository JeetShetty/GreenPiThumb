import contextlib
import datetime
import os
import shutil
import sqlite3
import tempfile
import unittest

import mock
from dateutil import tz
import pytz

from greenpithumb import db_store

# Timezone offset info for EST (UTC minus 5 hours).
UTC_MINUS_5 = tz.tzoffset(None, -18000)


class OpenOrCreateTest(unittest.TestCase):

    def setUp(self):
        self._temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self._temp_dir)

    @mock.patch.object(sqlite3, 'connect')
    def test_does_not_initialize_existing_db_file(self, mock_connect):
        mock_connection = mock.Mock()
        mock_connect.return_value = mock_connection
        # Simulate an existing database file
        with tempfile.NamedTemporaryFile() as temp_file:
            with contextlib.closing(db_store.open_or_create_db(temp_file.name)):
                mock_connect.assert_called_once_with(temp_file.name)
        # If the database already existed, we should not do anything except
        # call sqlite3.connect().
        mock_connection.cursor.assert_not_called()
        mock_connection.commit.assert_not_called()

    def test_creates_file_and_tables_when_db_does_not_already_exist(self):
        # Create a path for a file that does not already exist.
        db_path = os.path.join(self._temp_dir, 'test.db')
        with contextlib.closing(db_store.open_or_create_db(
                db_path)) as connection:
            cursor = connection.cursor()
            # Insertions into all tables should work after initialization.
            cursor.execute('INSERT INTO temperature VALUES (?, ?)',
                           ('2016-07-23T10:51:09.928000+00:00', 98.6))
            cursor.execute('INSERT INTO ambient_humidity VALUES (?, ?)',
                           ('2016-07-23T10:51:09.928000+00:00', 93.7))
            cursor.execute('INSERT INTO soil_moisture VALUES (?, ?)',
                           ('2016-07-23T10:51:09.928000+00:00', 57))
            cursor.execute('INSERT INTO ambient_light VALUES (?, ?)',
                           ('2016-07-23T10:51:09.928000+00:00', 75.2))
            cursor.execute('INSERT INTO watering_events VALUES (?, ?)',
                           ('2016-07-23T10:51:09.928000+00:00', 258.9))
            connection.commit()


class StoreClassesTest(unittest.TestCase):

    def test_store_soil_moisture(self):
        """Should insert timestamp and moisture level into database."""
        record = db_store.SoilMoistureRecord(
            timestamp=datetime.datetime(
                2016, 7, 23, 10, 51, 9, 928000, tzinfo=pytz.utc),
            soil_moisture=300)
        mock_cursor = mock.Mock()
        store = db_store.SoilMoistureStore(mock_cursor)
        store.store_soil_moisture(record)
        mock_cursor.execute.assert_called_once_with(
            'INSERT INTO soil_moisture VALUES (?, ?)', (
                '2016-07-23T10:51:09.928000+00:00', 300))

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
        ambient_light_record = db_store.AmbientLightRecord(
            timestamp=datetime.datetime(
                2016, 7, 23, 10, 51, 9, 928000, tzinfo=pytz.utc),
            ambient_light=50.0)
        mock_cursor = mock.Mock()
        store = db_store.AmbientLightStore(mock_cursor)
        store.store_ambient_light(ambient_light_record)
        mock_cursor.execute.assert_called_once_with(
            'INSERT INTO ambient_light VALUES (?, ?)', (
                '2016-07-23T10:51:09.928000+00:00', 50.0))

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
        humidity_record = db_store.HumidityRecord(
            timestamp=datetime.datetime(
                2016, 7, 23, 10, 51, 9, 928000, tzinfo=pytz.utc),
            humidity=50.0)
        mock_cursor = mock.Mock()
        store = db_store.HumidityStore(mock_cursor)
        store.store_humidity(humidity_record)
        mock_cursor.execute.assert_called_once_with(
            'INSERT INTO ambient_humidity VALUES (?, ?)',
            ('2016-07-23T10:51:09.928000+00:00', 50.0))

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

    def test_store_temperature(self):
        """Should insert timestamp and temperature into database."""
        temperature_record = db_store.TemperatureRecord(
            timestamp=datetime.datetime(
                2016, 7, 23, 10, 51, 9, 928000, tzinfo=pytz.utc),
            temperature=21.1)
        mock_cursor = mock.Mock()
        store = db_store.TemperatureStore(mock_cursor)
        store.store_temperature(temperature_record)
        mock_cursor.execute.assert_called_once_with(
            'INSERT INTO temperature VALUES (?, ?)',
            ('2016-07-23T10:51:09.928000+00:00', 21.1))

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
        watering_event_record = db_store.WateringEventRecord(
            timestamp=datetime.datetime(
                2016, 7, 23, 10, 51, 9, 928000, tzinfo=pytz.utc),
            water_pumped=200.0)
        mock_cursor = mock.Mock()
        store = db_store.WateringEventStore(mock_cursor)
        store.store_water_pumped(watering_event_record)
        mock_cursor.execute.assert_called_once_with(
            'INSERT INTO watering_events VALUES (?, ?)', (
                '2016-07-23T10:51:09.928000+00:00', 200.0))

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
