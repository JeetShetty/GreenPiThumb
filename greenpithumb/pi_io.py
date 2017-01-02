#import RPi.GPIO as GPIO


class IO(object):
    """Wrapper for input and output on a Raspberry Pi board.

    This wraps the board and allows the caller to read or send signals to
    the Raspberry Pi's pins. No more than one instance of this class should
    exist at any given time.
    """

    def __init__(self, gpio):
        """Creates a new input/output wrapper.

        Args:
            gpio: Raspberry Pi GPIO module.
        """
        self._GPIO = gpio
        self._output_pins = set()

    def turn_pin_on(self, pin):
        """Turns on a Raspberry Pi GPIO pin.

        Args:
            pin: Index of Raspberry Pi pin to turn on
        """
        self._ensure_pin_is_output(pin)
        self._GPIO.output(pin, self._GPIO.HIGH)

    def turn_pin_off(self, pin):
        """Turns off a Raspberry Pi GPIO pin.

        Args:
            pin: Index of Raspberry Pi pin to turn on
        """
        self._ensure_pin_is_output(pin)
        self._GPIO.output(pin, self._GPIO.LOW)

    def _ensure_pin_is_output(self, pin):
        """Adds pin to output pin set if it is not already in it."""
        if pin in self._output_pins:
            return
        self._GPIO.setup(pin, self._GPIO.OUT)
        self._output_pins.add(pin)

    def close(self):
        """Cleans up the Raspberry Pi I/O interface.

        Should be called when use of the I/O interface is complete.
        """
        self._GPIO.cleanup()