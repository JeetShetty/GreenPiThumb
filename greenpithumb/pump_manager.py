"""Pump Manager manages the water pump."""

# If soil goes below this moisture threshold, pump needs to add water.
# Moisture is based on sensor calibration by @dicksondisckson:
# https://github.com/dicksondickson/PlantFriends/blob/master/sensor_node/RFM69/sensor_node.ino
SOIL_MOISTURE_THRESHOLD = 300

# Default amount of water to add to the plant (in mL) when pump manager detects
# low soil moisture.
DEFAULT_PUMP_AMOUNT = 200


class PumpManager(object):

    def __init__(self, moisture_sensor, pump):
        """Creates a PumpManager object, which manages moisture levels.

        Args:
            moisture_sensor: A moisture sensor instance that provides soil
                moisture level readings.
            pump: A pump instance, which supports water pumping.
        """
        self._moisture_sensor = moisture_sensor
        self._pump = pump

    def pump_if_needed(self):
        """Run the water pump if there is a need to run it.

        Checks whether it's time to run the pump and runs it if needed.
        Running the pump is necessary if the soil's moisture is below the
        defined moisture threshold.

        """
        # TODO(JeetShetty): Add logic here so that it only runs the pump when
        # the soil moisture is too low.
        if self._moisture_sensor.moisture() < SOIL_MOISTURE_THRESHOLD:
            self._pump.pump_water(DEFAULT_PUMP_AMOUNT)
