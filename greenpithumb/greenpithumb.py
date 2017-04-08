import argparse
import contextlib
import logging
import Queue
import time

import Adafruit_DHT
import Adafruit_MCP3008
import picamera
import RPi.GPIO as GPIO

import adc_thread_safe
import camera_manager
import clock
import db_store
import dht11
import humidity_sensor
import light_sensor
import moisture_sensor
import pi_io
import poller
import pump
import record_processor
import sleep_windows
import temperature_sensor
import wiring_config_parser

logger = logging.getLogger(__name__)



def make_sensor_pollers(poll_interval, wiring_config, moisture_threshold,
                        record_queue, sleep_windows, raspberry_pi_io):
    logger.info('creating sensor pollers (poll interval=%d")', poll_interval)
    utc_clock = clock.Clock()
    local_clock = clock.LocalClock()
    # The MCP3008 spec and Adafruit library use different naming for the
    # Raspberry Pi GPIO pins, so we translate as follows:
    # * CLK -> CLK
    # * CS/SHDN -> CS
    # * DOUT -> MISO
    # * DIN -> MOSI
    adc = adc_thread_safe.Adc(
        Adafruit_MCP3008.MCP3008(
            clk=wiring_config.gpio_pins.mcp3008_clk,
            cs=wiring_config.gpio_pins.mcp3008_cs_shdn,
            miso=wiring_config.gpio_pins.mcp3008_dout,
            mosi=wiring_config.gpio_pins.mcp3008_din))
    local_dht11 = dht11.CachingDHT11(
        lambda: Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, wiring_config.gpio_pins.dht11),
        utc_clock)
    water_pump = pump.Pump(raspberry_pi_io, utc_clock,
                           wiring_config.gpio_pins.pump)
    pump_scheduler = pump.PumpScheduler(local_clock, sleep_windows)
    pump_manager = pump.PumpManager(water_pump, pump_scheduler,
                                    moisture_threshold)

    poller_factory = poller.SensorPollerFactory(utc_clock, poll_interval,
                                                record_queue)

    return [
        poller_factory.create_temperature_poller(
            temperature_sensor.TemperatureSensor(local_dht11)),
        poller_factory.create_humidity_poller(
            humidity_sensor.HumiditySensor(local_dht11)),
        poller_factory.create_soil_watering_poller(
            moisture_sensor.MoistureSensor(
                adc,
                pi_io.IO(GPIO), wiring_config.adc_channels.soil_moisture_sensor,
                wiring_config.gpio_pins.soil_moisture_1,
                wiring_config.gpio_pins.soil_moisture_2, utc_clock),
            pump_manager),
        poller_factory.create_ambient_light_poller(
            light_sensor.LightSensor(adc,
                                     wiring_config.adc_channels.light_sensor)),
    ]


def make_camera_poller(photo_interval, image_path, record_queue):
    utc_clock = clock.Clock()
    poller_factory = poller.SensorPollerFactory(utc_clock, photo_interval,
                                                record_queue)
    return poller_factory.create_camera_poller(
        camera_manager.CameraManager(
            image_path,
            utc_clock,
            picamera.PiCamera(resolution=picamera.PiCamera.MAX_RESOLUTION)))


def read_wiring_config(config_filename):
    logger.info('reading wiring config at "%s"', config_filename)
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


def configure_logging(verbose):
    """Configure the root logger for log output."""
    root_logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s %(name)-15s %(levelname)-4s %(message)s',
        '%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    if verbose:
        root_logger.setLevel(logging.INFO)
    else:
        root_logger.setLevel(logging.WARNING)


def main(args):
    configure_logging(args.verbose)
    logger.info('starting greenpithumb')
    wiring_config = read_wiring_config(args.config_file)
    record_queue = Queue.Queue()
    parsed_windows = sleep_windows.parse(args.sleep_window)
    raspberry_pi_io = pi_io.IO(GPIO)
    pollers = make_sensor_pollers(args.poll_interval, wiring_config,
                                  args.moisture_threshold, record_queue,
                                  parsed_windows, raspberry_pi_io)
    pollers.append(
        make_camera_poller(args.photo_interval, args.image_path, record_queue))
    with contextlib.closing(db_store.open_or_create_db(
            args.db_file)) as db_connection:
        record_processor = create_record_processor(db_connection, record_queue)
        try:
            for current_poller in pollers:
                current_poller.start_polling_async()
            while True:
                if not record_processor.try_process_next_record():
                    time.sleep(0.1)
        except KeyboardInterrupt:
            logger.info('Caught keyboard interrupt. Exiting.')
        finally:
            for current_poller in pollers:
                current_poller.close()
            raspberry_pi_io.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='GreenPiThumb',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-p',
        '--poll_interval',
        type=float,
        help='Number of minutes between each sensor poll',
        default=15)
    parser.add_argument(
        '-t',
        '--photo_interval',
        type=float,
        help='Number of minutes between each camera photo',
        default=(4 * 60))
    parser.add_argument(
        '-c',
        '--config_file',
        help='Wiring config file',
        default='greenpithumb/wiring_config.ini')
    parser.add_argument(
        '-s',
        '--sleep_window',
        action='append',
        type=str,
        default=[],
        help=('Time window during which GreenPiThumb will not activate its '
              'pump. Window should be in the form of a time range in 24-hour '
              'format, such as "03:15-03:45 (in the local time zone)"'))
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
    parser.add_argument(
        '-m',
        '--moisture_threshold',
        type=int,
        help=('Moisture threshold to start pump. The pump will turn on if the '
              'moisture level drops below this level'),
        default=900)
    parser.add_argument(
        '-v', '--verbose', action='store_true', help='Use verbose logging')
    main(parser.parse_args())
