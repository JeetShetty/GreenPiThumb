import db_store


class Error(Exception):
    pass


class UnsupportedRecordError(Error):
    pass


class RecordProcessor(object):
    """Stores records from a queue into database stores."""

    def __init__(self, record_queue, soil_moisture_store, ambient_light_store,
                 humidity_store, temperature_store, watering_event_store):
        self._record_queue = record_queue
        self._soil_moisture_store = soil_moisture_store
        self._ambient_light_store = ambient_light_store
        self._humidity_store = humidity_store
        self._temperature_store = temperature_store
        self._watering_event_store = watering_event_store

    def process_next_record(self):
        """Processes the next record from the queue, placing it in a store.

        Retrieves the next item from the queue (blocking until one is
        available) and then places it in the appropriate database store for its
        record type.

        Must be called from the same thread from which the database connections
        were created.
        """
        record = self._record_queue.get()
        if isinstance(record, db_store.SoilMoistureRecord):
            self._soil_moisture_store.insert(record)
        elif isinstance(record, db_store.AmbientLightRecord):
            self._ambient_light_store.insert(record)
        elif isinstance(record, db_store.HumidityRecord):
            self._humidity_store.insert(record)
        elif isinstance(record, db_store.TemperatureRecord):
            self._temperature_store.insert(record)
        elif isinstance(record, db_store.WateringEventRecord):
            self._watering_event_store.insert(record)
        else:
            raise UnsupportedRecordError('Unrecognized record type: %s' %
                                         str(record))
