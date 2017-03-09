import collections
from dateutil import parser


def _serialize_timestamp(timestamp):
    """Converts a timestamp to a string.

    Args:
        timestamp: Timestamp as a datetime object.

    Returns:
        Timestamp as a string in ISO 8601 format.
    """
    return timestamp.isoformat('T')


class DbStoreBase(object):
    """Base class for storing information in a database."""

    def __init__(self, cursor):
        """Creates a new DbStoreBase object for storing information.

        Args:
            cursor: SQLite database cursor.
        """
        self._cursor = cursor


class SoilMoistureStore(DbStoreBase):
    """Stores and retrieves timestamp and soil moisture readings."""

    def store_soil_moisture(self, timestamp, soil_moisture):
        """Inserts moisture and timestamp info into an SQLite database.

        Args:
            timestamp: A datetime object representing the time of the soil
                moisture reading.
            soil_moisture: An int of the soil moisture reading.
        """
        self._cursor.execute('INSERT INTO soil_moisture VALUES (?, ?)',
                             (_serialize_timestamp(timestamp), soil_moisture))

    def latest_soil_moisture(self):
        """Returns the most recent soil moisture reading."""
        query = '''SELECT soil_moisture FROM soil_moisture
                ORDER BY timestamp DESC
                LIMIT 1;'''

        self._cursor.execute(query)
        results = self._cursor.fetchall()
        if not results:
            return None
        else:
            return results[0][0]

    def retrieve_soil_moisture(self):
        """Retrieves timestamp and soil moisture readings.

        Returns:
            A list of objects with 'timestamp' and 'soil_moisture' fields.
        """
        self._cursor.execute('SELECT * FROM soil_moisture')
        data = []
        for row in self._cursor.fetchall():
            data.append((parser.parse(row[0]), row[1]))
        SoilMoistureRecord = collections.namedtuple(
            'SoilMoistureRecord', ['timestamp', 'soil_moisture'])
        soil_moisture_data = map(SoilMoistureRecord._make, data)
        return soil_moisture_data


class AmbientLightStore(DbStoreBase):
    """Stores timestamp and ambient light readings."""

    def store_ambient_light(self, timestamp, ambient_light):
        """Inserts ambient light and timestamp info into an SQLite database.

        Args:
            timestamp: A datetime object representing the time of the ambient
                light reading.
            ambient_light: A float of the ambient light level.
        """
        self._cursor.execute('INSERT INTO ambient_light VALUES (?, ?)',
                             (_serialize_timestamp(timestamp), ambient_light))

    def retrieve_ambient_light(self):
        """Retrieves timestamp and ambient light readings.

        Returns:
            A list of objects with 'timestamp' and 'ambient_light' fields.
        """
        self._cursor.execute('SELECT * FROM ambient_light')
        data = []
        for row in self._cursor.fetchall():
            data.append((parser.parse(row[0]), row[1]))
        AmbientLightRecord = collections.namedtuple(
            'AmbientLightRecord', ['timestamp', 'ambient_light'])
        ambient_light_data = map(AmbientLightRecord._make, data)
        return ambient_light_data


class HumidityStore(DbStoreBase):
    """Stores timestamp and ambient humidity readings."""

    def store_humidity(self, timestamp, humidity):
        """Inserts humidity and timestamp info into an SQLite database.

        Args:
            timestamp: A datetime object representing the time of the
                humidity reading.
            humidity: A float of the humidity reading.
        """
        self._cursor.execute('INSERT INTO ambient_humidity VALUES (?, ?)',
                             (_serialize_timestamp(timestamp), humidity))

    def retrieve_humidity(self):
        """Retrieves timestamp and relative humidity readings.

        Returns:
            A list of objects with 'timestamp' and 'humidity' fields.
        """
        self._cursor.execute('SELECT * FROM ambient_humidity')
        data = []
        for row in self._cursor.fetchall():
            data.append((parser.parse(row[0]), row[1]))
        HumidityRecord = collections.namedtuple('HumidityRecord',
                                                ['timestamp', 'humidity'])
        humidity_data = map(HumidityRecord._make, data)
        return humidity_data


class TemperatureStore(DbStoreBase):
    """Stores timestamp and ambient temperature readings."""

    def store_temperature(self, timestamp, temperature):
        """Inserts temperature and timestamp info into an SQLite database.

        Args:
            timestamp: A datetime object representing the time of the
                temperature reading.
            temperature: A float of the temperature reading in Celsius.
        """
        self._cursor.execute('INSERT INTO temperature VALUES (?, ?)',
                             (_serialize_timestamp(timestamp), temperature))

    def retrieve_temperature(self):
        """Retrieves timestamp and temperature(C) readings.

        Returns:
            A list of objects with 'timestamp' and 'temperature' fields.
        """
        self._cursor.execute('SELECT * FROM temperature')
        data = []
        for row in self._cursor.fetchall():
            data.append((parser.parse(row[0]), row[1]))
        TemperatureRecord = collections.namedtuple('TemperatureRecord',
                                                   ['timestamp', 'temperature'])
        temperature_data = map(TemperatureRecord._make, data)
        return temperature_data


class WateringEventStore(DbStoreBase):
    """Stores timestamp and volume of water pumped to plant."""

    def store_water_pumped(self, timestamp, water_pumped):
        """Inserts water volume and timestamp info into an SQLite database.

        Args:
            timestamp: A datetime object representing the time of the reading.
            water_pumped: A float of the water volume pumped in mL.
        """
        self._cursor.execute('INSERT INTO watering_events VALUES (?, ?)',
                             (_serialize_timestamp(timestamp), water_pumped))

    def retrieve_water_pumped(self):
        """Retrieves timestamp and volume of water pumped(in mL).

        Returns:
            A list of objects with 'timestamp' and 'water_pumped' fields.
        """
        self._cursor.execute('SELECT * FROM watering_events')
        data = []
        for row in self._cursor.fetchall():
            data.append((parser.parse(row[0]), row[1]))
        WateringEventRecord = collections.namedtuple(
            'WateringEventRecord', ['timestamp', 'water_pumped'])
        watering_event_data = map(WateringEventRecord._make, data)
        return watering_event_data
