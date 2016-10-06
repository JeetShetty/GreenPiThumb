class DbStoreBase(object):
    """Base class for storing information in a database."""

    def __init__(self, cursor):
        """Creates a new DbStoreBase object for storing information.

        Args:
            cursor: SQLite database cursor.
        """
        self._cursor = cursor


class SoilMoistureStore(DbStoreBase):
    """Stores timestamp and soil moisture readings."""

    def store_soil_moisture(self, timestamp, soil_moisture):
        """Inserts moisture and timestamp info into an SQLite database.

        Args:
            timestamp: A datetime object representing the time of the soil
                moisture reading.
            soil_moisture: An int of the soil moisture reading.
        """
        self._cursor.execute('INSERT INTO soil_moisture VALUES (?, ?)',
                             (timestamp, soil_moisture))

    def get_latest_soil_moisture(self):
        """Returns the most recent soil moisture reading."""
        query = '''SELECT soil_moisture FROM soil_moisture
                ORDER BY timestamp DESC
                LIMIT 1;'''

        self._cursor.execute(query)
        results = self._cursor.fetchall()
        if results == []:
            return None
        else:
            return results[0][0]


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
                             (timestamp, ambient_light))


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
                             (timestamp, humidity))


class ReservoirLevelStore(DbStoreBase):
    """Stores timestamp and reservoir level readings."""

    def store_reservoir_level(self, timestamp, reservoir_level):
        """Inserts reservoir level and timestamp info into an SQLite database.

        Args:
            timestamp: A datetime object representing the time of the
                reservoir level reading.
            reservoir_level: A float of the reservoir level reading in mL.
        """
        self._cursor.execute('INSERT INTO reservoir_level VALUES (?, ?)',
                             (timestamp, reservoir_level))


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
                             (timestamp, temperature))


class WateringEventStore(DbStoreBase):
    """Stores timestamp and volume of water pumped to plant."""

    def store_water_pumped(self, timestamp, water_pumped):
        """Inserts water volume and timestamp info into an SQLite database.

        Args:
            timestamp: A datetime object representing the time of the reading.
            water_pumped: A float of the water volume pumped in mL.
        """
        self._cursor.execute('INSERT INTO watering_events VALUES (?, ?)',
                             (timestamp, water_pumped))
