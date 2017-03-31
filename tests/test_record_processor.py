import datetime
import Queue
import unittest

import mock
import pytz

from greenpithumb import db_store
from greenpithumb import record_processor


class RecordProcessorTest(unittest.TestCase):

    def setUp(self):
        self.record_queue = Queue.Queue()
        self.mock_soil_moisture_store = mock.Mock()
        self.mock_ambient_light_store = mock.Mock()
        self.mock_humidity_store = mock.Mock()
        self.mock_temperature_store = mock.Mock()
        self.mock_watering_event_store = mock.Mock()
        self.processor = record_processor.RecordProcessor(
            record_queue=self.record_queue,
            soil_moisture_store=self.mock_soil_moisture_store,
            ambient_light_store=self.mock_ambient_light_store,
            humidity_store=self.mock_humidity_store,
            temperature_store=self.mock_temperature_store,
            watering_event_store=self.mock_watering_event_store)

    def test_process_empty_queue_does_not_hang_or_raise_error(self):
        self.processor.try_process_next_record()

    def test_process_soil_moisture_record(self):
        record = db_store.SoilMoistureRecord(
            timestamp=datetime.datetime(
                2016, 7, 23, 10, 51, 9, 928000, tzinfo=pytz.utc),
            soil_moisture=300)
        self.record_queue.put(record)
        self.processor.try_process_next_record()
        self.mock_soil_moisture_store.insert.assert_called_with(record)

    def test_process_ambient_light_record(self):
        record = db_store.AmbientLightRecord(
            timestamp=datetime.datetime(
                2016, 7, 23, 10, 51, 9, 928000, tzinfo=pytz.utc),
            ambient_light=29.2)
        self.record_queue.put(record)
        self.processor.try_process_next_record()
        self.mock_ambient_light_store.insert.assert_called_with(record)

    def test_process_humidity_record(self):
        record = db_store.HumidityRecord(
            timestamp=datetime.datetime(
                2016, 7, 23, 10, 51, 9, 928000, tzinfo=pytz.utc),
            humidity=184.5)
        self.record_queue.put(record)
        self.processor.try_process_next_record()
        self.mock_humidity_store.insert.assert_called_with(record)

    def test_process_temperature_record(self):
        record = db_store.TemperatureRecord(
            timestamp=datetime.datetime(
                2016, 7, 23, 10, 51, 9, 928000, tzinfo=pytz.utc),
            temperature=32.9)
        self.record_queue.put(record)
        self.processor.try_process_next_record()
        self.mock_temperature_store.insert.assert_called_with(record)

    def test_process_watering_event_record(self):
        record = db_store.WateringEventRecord(
            timestamp=datetime.datetime(
                2016, 7, 23, 10, 51, 9, 928000, tzinfo=pytz.utc),
            water_pumped=15.6)
        self.record_queue.put(record)
        self.processor.try_process_next_record()
        self.mock_watering_event_store.insert.assert_called_with(record)

    def test_rejects_unsupported_record(self):
        record = 'dummy invalid record'
        self.record_queue.put(record)
        with self.assertRaises(record_processor.UnsupportedRecordError):
            self.processor.try_process_next_record()
