import argparse
import contextlib
import Queue

import Adafruit_DHT
import Adafruit_MCP3008
import picamera
import RPi.GPIO as GPIO

import camera_manager
import clock
import db_store
import dht11
import humidity_sensor
import light_sensor
import moisture_sensor
import pi_io
import record_processor
import temperature_sensor
import wiring_config_parser


# TODO(mtlynch): Rewrite this code so it's hooked up to the pollers.
class SensorHarness(object):
    """Simple container for GreenPiThumbs sensors."""

    def __init__(self, wiring_config, image_path):
        local_clock = clock.LocalClock()
        # The MCP3008 spec and Adafruit library use different naming for the
        # Raspberry Pi GPIO pins, so we translate as follows:
        # * CLK -> CLK
        # * CS/SHDN -> CS
        # * DOUT -> MISO
        # * DIN -> MOSI
        self._adc = Adafruit_MCP3008.MCP3008(
            clk=wiring_config.gpio_pins.mcp3008_clk,
            cs=wiring_config.gpio_pins.mcp3008_cs_shdn,
            miso=wiring_config.gpio_pins.mcp3008_dout,
            mosi=wiring_config.gpio_pins.mcp3008_din)
        self._light_sensor = light_sensor.LightSensor(
            self._adc, wiring_config.adc_channels.light_sensor)
        self._moisture_sensor = moisture_sensor.MoistureSensor(
            self._adc,
            pi_io.IO(GPIO), wiring_config.adc_channels.soil_moisture_sensor,
            wiring_config.gpio_pins.soil_moisture_1,
            wiring_config.gpio_pins.soil_moisture_2, local_clock)
        self._dht11 = dht11.CachingDHT11(
            lambda: Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, wiring_config.gpio_pins.dht11),
            local_clock)
        self._temperature_sensor = temperature_sensor.TemperatureSensor(
            self._dht11)
        self._humidity_sensor = humidity_sensor.HumiditySensor(self._dht11)
        self._camera_manager = camera_manager.CameraManager(image_path,
                                                            local_clock,
                                                            picamera.PiCamera())


def read_wiring_config(config_filename):
    with open(config_filename) as config_file:
        return wiring_config_parser.parse(config_file.read())


def create_record_processor(db_connection, record_queue):
    return record_processor.RecordProcessor(
        record_queue,
        db_store.SoilMoistureStore(db_connection),
        db_store.AmbientLightStore(db_connection),
        db_store.HumidityStore(db_connection),
        db_store.TemperatureStore(db_connection),
        db_store.WateringEventStore(db_connection))


def main(args):
    record_queue = Queue.Queue()
    with contextlib.closing(db_store.open_or_create_db(
            args.db_file)) as db_connection:
        record_processor = create_record_processor(db_connection, record_queue)
        while True:
            record_processor.process_next_record()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='GreenPiThumb',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-p',
        '--poll_interval',
        type=float,
        help='Number of seconds between each sensor poll',
        default=0.5)
    parser.add_argument(
        '-c',
        '--config_file',
        help='Wiring config file',
        default='wiring_config.ini')
    parser.add_argument(
        '-s',
        '--sleep_window',
        action='append',
        type=str,
        help=('Time window during which GreenPiThumb will not activate its '
              'pump. Window should be in the form of a time range in 24-hour '
              'format, such as "03:15-03:45"'))
    parser.add_argument(
        '-i',
        '--image_path',
        type=str,
        help='Path to folder where images will be stored',
        default='images/')
    parser.add_argument(
        '-d',
        '--db_file',
        help='Location to store GreenPiThumb database file',
        default='greenpithumb/greenpithumb.db')
    main(parser.parse_args())
