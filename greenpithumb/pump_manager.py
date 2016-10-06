# If soil goes below this moisture threshold, pump needs to add water.
# Moisture is based on sensor calibration by @dicksondisckson:
# https://github.com/dicksondickson/PlantFriends/blob/master/sensor_node/RFM69/sensor_node.ino
SOIL_MOISTURE_THRESHOLD = 300

# Default amount of water to add to the plant (in mL) when pump manager detects
# low soil moisture.
DEFAULT_PUMP_AMOUNT = 200


class PumpManager(object):
    """Pump Manager manages the water pump."""

    def __init__(self, pump, pump_scheduler):
        """Creates a PumpManager object, which manages a water pump.

        Args:
            pump: A pump instance, which supports water pumping.
            pump_scheduler: A pump scheduler instance that controls the time
                periods in which the pump can be run.
        """
        self._pump = pump
        self._pump_scheduler = pump_scheduler

    def pump_if_needed(self, moisture):
        """Run the water pump if there is a need to run it.

        Checks whether it's time to run the pump and runs it if needed and
        allowed. Running the pump is necessary if the soil's moisture is below
        the defined moisture threshold. Returns a float of the amount of water
        pumped, in ml.

        Args:
            moisture: Soil moisture level
        """
        if self._pump_scheduler.is_running_pump_allowed():
            if moisture < SOIL_MOISTURE_THRESHOLD:
                pump_amount = DEFAULT_PUMP_AMOUNT
                self._pump.pump_water(pump_amount)
                return pump_amount

        return 0
