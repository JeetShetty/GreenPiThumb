import unittest

from greenpithumb import wiring_config_parser


class WiringConfigParserTest(unittest.TestCase):

    def test_empty_config_is_invalid(self):
        with self.assertRaises(wiring_config_parser.InvalidConfigError):
            wiring_config_parser.parse('')

    def test_full_config_parses_successfully(self):
        wiring_config = wiring_config_parser.parse("""
[gpio_pins]
pump: 26
dht11: 21
soil_moisture_1: 16
soil_moisture_2: 12
mcp3008_clk: 18
mcp3008_dout: 23
mcp3008_din: 24
mcp3008_cs_shdn: 25

[adc_channels]
soil_moisture_sensor: 0
light_sensor: 6
""")
        self.assertEquals(wiring_config.gpio_pins.pump, 26)
        self.assertEquals(wiring_config.gpio_pins.dht11, 21)
        self.assertEquals(wiring_config.gpio_pins.soil_moisture_1, 16)
        self.assertEquals(wiring_config.gpio_pins.soil_moisture_2, 12)
        self.assertEquals(wiring_config.gpio_pins.mcp3008_clk, 18)
        self.assertEquals(wiring_config.gpio_pins.mcp3008_dout, 23)
        self.assertEquals(wiring_config.gpio_pins.mcp3008_din, 24)
        self.assertEquals(wiring_config.gpio_pins.mcp3008_cs_shdn, 25)
        self.assertEquals(wiring_config.adc_channels.soil_moisture_sensor, 0)
        self.assertEquals(wiring_config.adc_channels.light_sensor, 6)

    def test_config_is_invalid_if_required_settings_missing(self):
        with self.assertRaises(wiring_config_parser.InvalidConfigError):
            wiring_config_parser.parse("""
[gpio_pins]
pump: 26
dht11: 21
soil_moisture_1: 16
soil_moisture_2: 12
mcp3008_clk: 18
mcp3008_dout: 23
mcp3008_din: 24

# Required setting is commented out
# mcp3008_cs_shdn: 25

[adc_channels]
soil_moisture_sensor: 0
light_sensor: 6
""")

    def test_rejects_too_low_gpio_pin_number(self):
        with self.assertRaises(wiring_config_parser.IllegalGpioPinNumberError):
            wiring_config_parser.parse("""
[gpio_pins]

dht11: 21
mcp3008_clk: 18
mcp3008_dout: 23
mcp3008_din: 24
mcp3008_cs_shdn: 25

# illegal: GPIO pin must correspond to a pin that exists on the Raspberry Pi
pump: 1

[adc_channels]
soil_moisture_sensor: 0
light_sensor: 6
""")

    def test_rejects_too_high_gpio_pin_number(self):
        with self.assertRaises(wiring_config_parser.IllegalGpioPinNumberError):
            wiring_config_parser.parse("""
[gpio_pins]

dht11: 21
soil_moisture_1: 16
soil_moisture_2: 12
mcp3008_clk: 18
mcp3008_dout: 23
mcp3008_din: 24
mcp3008_cs_shdn: 25

# illegal: GPIO pin must correspond to a pin that exists on the Raspberry Pi
pump: 28

[adc_channels]
soil_moisture_sensor: 0
light_sensor: 6
""")

    def test_rejects_non_numeric_gpio_pin_number(self):
        with self.assertRaises(wiring_config_parser.IllegalGpioPinNumberError):
            wiring_config_parser.parse("""
[gpio_pins]
dht11: 21
soil_moisture_1: 16
soil_moisture_2: 12
mcp3008_clk: 18
mcp3008_dout: 23
mcp3008_din: 24
mcp3008_cs_shdn: 25

# illegal: GPIO pin must be a number
pump: banana

[adc_channels]
soil_moisture_sensor: 0
light_sensor: 6
""")

    def test_rejects_duplicate_gpio_pins(self):
        with self.assertRaises(
                wiring_config_parser.DuplicateGpioPinNumberError):
            wiring_config_parser.parse("""
[gpio_pins]
pump: 26
dht11: 21
soil_moisture_1: 16
soil_moisture_2: 12
mcp3008_clk: 18
mcp3008_dout: 23
mcp3008_din: 24

# illegal: re-uses pin from pump
mcp3008_cs_shdn: 26

[adc_channels]
soil_moisture_sensor: 0
light_sensor: 6
""")

    def test_rejects_too_low_adc_channel(self):
        with self.assertRaises(wiring_config_parser.IllegalAdcChannelError):
            wiring_config_parser.parse("""
[gpio_pins]
pump: 26
dht11: 21
soil_moisture_1: 16
soil_moisture_2: 12
mcp3008_clk: 18
mcp3008_dout: 23
mcp3008_din: 24
mcp3008_cs_shdn: 25

[adc_channels]
light_sensor: 6

# illegal: ADC channels are from 0 to 7
soil_moisture_sensor: -1
""")

    def test_rejects_too_high_adc_channel(self):
        with self.assertRaises(wiring_config_parser.IllegalAdcChannelError):
            wiring_config_parser.parse("""
[gpio_pins]
pump: 26
dht11: 21
soil_moisture_1: 16
soil_moisture_2: 12
mcp3008_clk: 18
mcp3008_dout: 23
mcp3008_din: 24
mcp3008_cs_shdn: 25

[adc_channels]
light_sensor: 6

# illegal: ADC channels are from 0 to 7
soil_moisture_sensor: 8
""")

    def test_rejects_non_numeric_adc_channel(self):
        with self.assertRaises(wiring_config_parser.IllegalAdcChannelError):
            wiring_config_parser.parse("""
[gpio_pins]
pump: 26
dht11: 21
soil_moisture_1: 16
soil_moisture_2: 12
mcp3008_clk: 18
mcp3008_dout: 23
mcp3008_din: 24
mcp3008_cs_shdn: 25

[adc_channels]
light_sensor: 6

# illegal: ADC channels are numeric
soil_moisture_sensor: banana
""")

    def test_rejects_duplicate_adc_channel(self):
        with self.assertRaises(wiring_config_parser.DuplicateAdcChannelError):
            wiring_config_parser.parse("""
[gpio_pins]
pump: 26
dht11: 21
soil_moisture_1: 16
soil_moisture_2: 12
mcp3008_clk: 18
mcp3008_dout: 23
mcp3008_din: 24
mcp3008_cs_shdn: 25

[adc_channels]
light_sensor: 6

# illegal: re-uses channel from light_sensor
soil_moisture_sensor: 6
""")
