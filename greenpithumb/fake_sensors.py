"""Collection of fake sensosrs to use until we switch to real hardware."""

# TODO(mtlynch): Delete this once we move to real hardware.

import random

import adc
from dht11 import dht11


class FakeAdc(adc.Adc):
    """Fake ADC to use (temporarily) until we switch to real hardware.

    Fake implementation of an ADC. Generates random readings.
    """

    def __init__(self, light_start, moisture_start):
        self._pin_values = {
            adc.PIN_LIGHT_SENSOR: light_start,
            adc.PIN_MOISTURE_SENSOR: moisture_start,
        }

    def read_pin(self, pin):
        self._pin_values[pin] += random.randint(-5, 5)
        return self._pin_values[pin]


class FakeDht11(object):

    def __init__(self, temperature_start, humidity_start):
        self._temperature = temperature_start
        self._humidity = humidity_start

    def read(self):
        self._temperature += random.randint(-5, 5)
        self._humidity += random.randint(-5, 5)

        return dht11.DHT11Result(error_code=dht11.DHT11Result.ERR_NO_ERROR,
                                 temperature=self._temperature,
                                 humidity=self._humidity)
