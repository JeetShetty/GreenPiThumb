import collections
import ConfigParser
import io


class Error(Exception):
    pass


class InvalidConfigError(Error):
    """Indicates an error parsing a GreenPiThumb wiring config."""
    pass


class IllegalGpioPinNumberError(Error):
    """Indicates an attempt to parse a GPIO pin with an invalid value."""


class IllegalAdcChannelError(Error):
    """Indicates an attempt to parse an ADC channel with an invalid value."""


class DuplicateGpioPinNumberError(Error):
    """Indicates an attempt to parse a GPIO pin with an invalid value."""


class DuplicateAdcChannelError(Error):
    """Indicates an attempt to parse an ADC channel with an invalid value."""


# Represents GreenPiThumb's Rapsberry Pi GPIO pin configuration.
_GpioPinConfig = collections.namedtuple('_GpioPinConfig', [
    'pump', 'dht11', 'soil_moisture_1', 'soil_moisture_2', 'mcp3008_clk',
    'mcp3008_dout', 'mcp3008_din', 'mcp3008_cs_shdn'
])


def _validate_gpio_pin_config(gpio_config):
    """Validates a GPIO pin configuration.

    Args:
        gpio_config: The GPIO configuration object to validate.

    Raises:
        DuplicateGpioPinNumberError when the same GPIO pin is assigned to
            multiple components.
    """
    used_pins = set()
    for pin in [
            gpio_config.pump, gpio_config.dht11, gpio_config.mcp3008_clk,
            gpio_config.mcp3008_dout, gpio_config.mcp3008_din,
            gpio_config.mcp3008_cs_shdn
    ]:
        if pin in used_pins:
            raise DuplicateGpioPinNumberError(
                'GPIO pin cannot be assigned to multiple components: %d' % pin)
        used_pins.add(pin)


class _AdcChannelConfig(object):
    """Represents GreenPiThumb's ADC channel configuration."""

    def __init__(self, soil_moisture_sensor, light_sensor):
        self._soil_moisture_sensor = soil_moisture_sensor
        self._light_sensor = light_sensor

    @property
    def soil_moisture_sensor(self):
        return self._soil_moisture_sensor

    @property
    def light_sensor(self):
        return self._light_sensor


def _validate_adc_channel_config(adc_config):
    """Validates an ADC channel configuration.

    Args:
        adc_config: The ADC channel configuration to validate

    Raises:
        DuplicateAdcChannelError when the same ADC channel is assigned to
            multiple components.
    """
    if adc_config.soil_moisture_sensor == adc_config.light_sensor:
        raise DuplicateAdcChannelError(
            'Soil moisture sensor and light sensor cannot have the same ADC '
            'channel: %d' % adc_config.soil_moisture_sensor)


class _WiringConfig(object):
    """Represents GreenPiThumb's wiring configuration."""

    def __init__(self, gpio_pin_config, adc_channel_config):
        self._gpio_pin_config = gpio_pin_config
        self._adc_channel_config = adc_channel_config

    @property
    def gpio_pins(self):
        return self._gpio_pin_config

    @property
    def adc_channels(self):
        return self._adc_channel_config


def _parse_gpio_pin(pin_raw):
    """Parses a GPIO pin value from the configuration file.

    Parses a GPIO pin value. Must be a valid Raspberry Pi GPIO pin number. Must
    be a value from 2 to 27.

    Args:
        pin_raw: The raw GPIO pin value from the configuration file.

    Returns:
        The parsed GPIO pin value as an int.

    Raises:
        IllegalGpioPinNumberError when the value is invalid.
    """
    try:
        pin = int(pin_raw)
    except ValueError:
        raise IllegalGpioPinNumberError(
            'Invalid GPIO pin: %s. Pin must be a value from 2 to 27. '
            'Be sure to use BCM numbering, not BOARD numbering.' % pin_raw)
    if not (2 <= pin <= 27):
        raise IllegalGpioPinNumberError(
            'Invalid GPIO pin: %s. Pin must be a value from 2 to 27. '
            'Be sure to use BCM numbering, not BOARD numbering.' % pin_raw)
    return pin


def _parse_adc_channel(channel_raw):
    """Parses an ADC channel value from the configuration file.

    Parses an ADC channel value. Must be a value from 0 to 7.

    Args:
        channel_raw: The raw ADC channel value from the configuration file.

    Returns:
        The parsed channel value as an int.

    Raises:
        IllegalAdcChannelError when the value is invalid.
    """
    try:
        channel = int(channel_raw)
    except ValueError:
        raise IllegalAdcChannelError(
            'Invalid ADC channel: %s. Channel must be a value from 0 to 7.' %
            channel_raw)
    if not (0 <= channel <= 7):
        raise IllegalAdcChannelError(
            'Invalid ADC channel: %s. Channel must be a value from 0 to 7.' %
            channel_raw)
    return channel


def parse(config_data):
    """Parse GreenPiThumb wiring configuration from text.

    Given the contents of a GreenPiThumb wiring configuration file, parses
    the configuration into a wiring config object.

    Args:
        config_data: The contents of a GreenPiThumb configuration file.

    Returns:
        A wiring configuration object with the following properties:
            * gpio_pins.pump
            * gpio_pins.dht11
            * gpio_pins.soil_moisture_1
            * gpio_pins.soil_moisture_2
            * gpio_pins.mcp3008_clk
            * gpio_pins.mcp3008_dout
            * gpio_pins.mcp3008_din
            * gpio_pins.mcp3008_cs_shdn
            * adc_channels.soil_moisture_sensor
            * adc_channels.light_sensor
    """
    raw_parser = ConfigParser.RawConfigParser()
    try:
        raw_parser.readfp(io.BytesIO(config_data))
        gpio_pin_config = _GpioPinConfig(
            pump=_parse_gpio_pin(raw_parser.get('gpio_pins', 'pump')),
            dht11=_parse_gpio_pin(raw_parser.get('gpio_pins', 'dht11')),
            mcp3008_clk=_parse_gpio_pin(
                raw_parser.get('gpio_pins', 'mcp3008_clk')),
            mcp3008_din=_parse_gpio_pin(
                raw_parser.get('gpio_pins', 'mcp3008_din')),
            mcp3008_dout=_parse_gpio_pin(
                raw_parser.get('gpio_pins', 'mcp3008_dout')),
            mcp3008_cs_shdn=_parse_gpio_pin(
                raw_parser.get('gpio_pins', 'mcp3008_cs_shdn')))
        _validate_gpio_pin_config(gpio_pin_config)
        adc_channel_config = _AdcChannelConfig(
            soil_moisture_sensor=_parse_adc_channel(
                raw_parser.get('adc_channels', 'soil_moisture_sensor')),
            light_sensor=_parse_adc_channel(
                raw_parser.get('adc_channels', 'light_sensor')))
        _validate_adc_channel_config(adc_channel_config)
        return _WiringConfig(gpio_pin_config, adc_channel_config)
    except ConfigParser.Error as ex:
        raise InvalidConfigError('Failed to parse wiring config', ex)
