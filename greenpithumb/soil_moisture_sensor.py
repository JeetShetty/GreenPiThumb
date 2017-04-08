import logging

logger = logging.getLogger(__name__)


class SoilMoistureSensor(object):
    """Wrapper for a moisture sensor."""

    def __init__(self, adc, pi_io, channel, gpio_pin_1, gpio_pin_2, clock):
        """Creates a new SoilMoistureSensor instance.

        Args:
            adc: ADC(analog to digital) interface to receive analog signals from
                moisture sensor.
            pi_io: Raspberry Pi I/O interface.
            channel: ADC channel to which the moisture sensor is connected. Must
                be an int between 0 and 7.
            gpio_pin_1: One of the Raspberry Pi GPIO pins that the moisture
                sensor is connected to. Must be an int between 2 and 27.
            gpio_pin_2: The other GPIO pin that the moisture sensor is connected
                to. Must be an int between 2 and 27.
            clock: Clock interface.
        """
        self._adc = adc
        self._pi_io = pi_io
        self._channel = channel
        self._gpio_pin_1 = gpio_pin_1
        self._gpio_pin_2 = gpio_pin_2
        self._clock = clock

    def soil_moisture(self):
        """Returns the soil moisture level.

        Takes two readings from the moisture sensor with the GPIO pins powering
        it alternately turned on and off (one in each state). Returns the
        average of the two readings.
        """
        try:
            self._pi_io.turn_pin_on(self._gpio_pin_1)
            self._pi_io.turn_pin_off(self._gpio_pin_2)
            moisture_one = self._adc.read_adc(self._channel)
            logger.info('soil moisture reading (1 of 2) = %d', moisture_one)

            # We need to turn off both pins before the sleep so that the charge
            # has time to dissipate before the next read.
            self._pi_io.turn_pin_off(self._gpio_pin_1)
            self._clock.wait(0.1)

            self._pi_io.turn_pin_on(self._gpio_pin_2)
            self._pi_io.turn_pin_off(self._gpio_pin_1)
            moisture_two = 1023 - self._adc.read_adc(self._channel)
            logger.info('soil moisture reading (2 of 2) = %d', moisture_two)

            return (moisture_one + moisture_two) / 2
        finally:
            self._pi_io.turn_pin_off(self._gpio_pin_1)
            self._pi_io.turn_pin_off(self._gpio_pin_2)
