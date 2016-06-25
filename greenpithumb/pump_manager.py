"""Pump Manager manages the water pump."""
# If soil goes below this moisture threshold, pump needs to add water.
# Moisture is based on sensor calibration by @dicksondisckson:
# https://github.com/dicksondickson/PlantFriends/blob/master/sensor_node/RFM69/sensor_node.ino
SOIL_MOISTURE_THRESHOLD = 300

# Default amount of water to add to the plant (in mL) when pump manager detects
# low soil moisture.
DEFAULT_PUMP_AMOUNT = 200


class PumpManager(object):

    def __init__(self, moisture_sensor, pump, pump_scheduler):
        """Creates a PumpManager object, which manages moisture levels.

        Args:
            moisture_sensor: A moisture sensor instance that provides soil
                moisture level readings.
            pump: A pump instance, which supports water pumping.
            pump_scheduler: A pump scheduler instance that controls the time
                periods in which the pump can be run.
        """
        self._moisture_sensor = moisture_sensor
        self._pump = pump
        self._pump_scheduler = pump_scheduler

    def pump_if_needed(self):
        """Run the water pump if there is a need to run it.

        Checks whether it's time to run the pump and runs it if needed.
        Running the pump is necessary if the soil's moisture is below the
        defined moisture threshold.
        """
        if self._pump_scheduler.is_running_pump_allowed():
            if self._moisture_sensor.moisture() < SOIL_MOISTURE_THRESHOLD:
                self._pump.pump_water(DEFAULT_PUMP_AMOUNT)
