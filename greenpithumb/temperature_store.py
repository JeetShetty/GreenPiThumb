class TemperatureStore(object):
    """Stores timestamp and ambient temperature readings."""

    def __init__(self, cursor):
        """Creates a TemperatureStore object, which stores temperature readings.

        Args:
            cursor: SQLite database cursor.
        """
        self._cursor = cursor

    def store_temperature(self, timestamp, temperature):
        """Inserts temperature and timestamp info into an  SQLite database.

        Args:
            timestamp: A datetime object representing the time of the
                temperature reading.
            temperature: A float of the temperature reading in Celsius.
        """
        self._cursor.execute('INSERT INTO temperature VALUES (?, ?)',
                             (timestamp, temperature))
