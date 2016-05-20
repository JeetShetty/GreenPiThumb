import argparse
import time

import fake_sensors
import humidity_sensor
import light_sensor
import moisture_sensor
import temperature_sensor


class SensorHarness(object):
    """Simple container for GreenPiThumbs that polls their values and prints."""

    def __init__(self):
        self._adc = fake_sensors.FakeAdc(light_start=500.0,
                                         moisture_start=600.0)
        self._light_sensor = light_sensor.LightSensor(self._adc)
        self._moisture_sensor = moisture_sensor.MoistureSensor(self._adc)
        self._dht11 = fake_sensors.FakeDht11(temperature_start=35.0,
                                             humidity_start=150.0)
        self._temperature_sensor = temperature_sensor.TemperatureSensor(
            self._dht11)
        self._humidity_sensor = humidity_sensor.HumiditySensor(self._dht11)

    def print_readings_header(self):
        """Print a header for sensor values to be printed in columns."""
        print 'light\tmoisture\ttemperature\thumidity'

    def print_readings(self):
        """Print sensor values in columns."""
        light_reading = '%.1f%%' % self._light_sensor.get_light_level()
        moisture_reading = '%.1f' % self._moisture_sensor.moisture()
        temperature_reading = (
            ('%1.f' %
             self._temperature_sensor.get_temperature()) + u'\N{DEGREE SIGN} C')
        humidity_reading = '%.1f' % self._humidity_sensor.get_humidity_level()
        print '%s\t%s\t\t%s\t\t%s' % (light_reading, moisture_reading,
                                      temperature_reading, humidity_reading)


def main(args):
    sensor_harness = SensorHarness()
    sensor_harness.print_readings_header()
    while True:
        sensor_harness.print_readings()
        time.sleep(args.poll_interval)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='GreenPiThumb',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-p',
                        '--poll_interval',
                        type=float,
                        help='Number of seconds between each sensor poll',
                        default=0.5)
    main(parser.parse_args())
