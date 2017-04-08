import Queue

import db_store


class Error(Exception):
    pass


class UnsupportedRecordError(Error):
    pass


class RecordProcessor(object):
    """Stores records from a queue into database stores."""

    def __init__(self, record_queue, soil_moisture_store, light_store,
                 humidity_store, temperature_store, watering_event_store):
        self._record_queue = record_queue
        self._soil_moisture_store = soil_moisture_store
        self._light_store = light_store
        self._humidity_store = humidity_store
        self._temperature_store = temperature_store
        self._watering_event_store = watering_event_store

    def try_process_next_record(self):
        """Processes the next record from the queue, placing it in a store.

        If an item is available in the queue, removes it and places it in the
        appropriate store. If no item is in the queue, returns immediately.

        Must be called from the same thread from which the database connections
        were created.

        Returns:
            True if it processed a record, False if the queue contained no
            records.

        Raises:
            UnsupportedRecordError if the queue contains an unexpected record
                type.
        """
        try:
            record = self._record_queue.get_nowait()
        except Queue.Empty:
            return False

        if isinstance(record, db_store.SoilMoistureRecord):
            self._soil_moisture_store.insert(record)
        elif isinstance(record, db_store.LightRecord):
            self._light_store.insert(record)
        elif isinstance(record, db_store.HumidityRecord):
            self._humidity_store.insert(record)
        elif isinstance(record, db_store.TemperatureRecord):
            self._temperature_store.insert(record)
        elif isinstance(record, db_store.WateringEventRecord):
            self._watering_event_store.insert(record)
        else:
            raise UnsupportedRecordError('Unrecognized record type: %s' %
                                         str(record))
        return True
