import logging

logger = logging.getLogger(__name__)

# Pump rate in mL/s (4.3 L/min)
_PUMP_RATE_ML_PER_SEC = 4300.0 / 60.0

# If soil goes below this moisture threshold, pump needs to add water.
# Moisture is based on sensor calibration by @dicksondisckson:
# https://github.com/dicksondickson/PlantFriends/blob/master/sensor_node/RFM69/sensor_node.ino
SOIL_MOISTURE_THRESHOLD = 300

# Default amount of water to add to the plant (in mL) when pump manager detects
# low soil moisture.
DEFAULT_PUMP_AMOUNT = 200


class Pump(object):
    """Wrapper for a Seaflo 12V water pump."""

    def __init__(self, pi_io, clock, pump_pin):
        """Creates a new Pump wrapper.

        Args:
            pi_io: Raspberry Pi I/O interface.
            clock: A clock interface.
            pump_pin: Raspberry Pi pin to which the pump is connected.
        """
        self._pi_io = pi_io
        self._clock = clock
        self._pump_pin = pump_pin

    def pump_water(self, amount_ml):
        """Pumps the specified amount of water.

        Args:
            amount_ml: Amount of water to pump (in mL).

        Raises:
            ValueError: The amount of water to be pumped is invalid.
        """
        if amount_ml == 0.0:
            return
        elif amount_ml < 0.0:
            raise ValueError('Cannot pump a negative amount of water')
        else:
            logger.info('turning pump on (with GPIO pin %d)', self._pump_pin)
            self._pi_io.turn_pin_on(self._pump_pin)

            wait_time_seconds = amount_ml / _PUMP_RATE_ML_PER_SEC
            self._clock.wait(wait_time_seconds)

            logger.info('turning pump off (with GPIO pin %d)', self._pump_pin)
            self._pi_io.turn_pin_off(self._pump_pin)
            logger.info('pumped %.f mL of water', amount_ml)

        return


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
        the defined moisture threshold.

        Args:
            moisture: Soil moisture level

        Returns:
            The amount of water pumped, in mL.
        """
        if self._pump_scheduler.is_running_pump_allowed():
            if moisture < SOIL_MOISTURE_THRESHOLD:
                pump_amount = DEFAULT_PUMP_AMOUNT
                self._pump.pump_water(pump_amount)
                return pump_amount

        return 0


class PumpScheduler(object):
    """Controls when the pump is allowed to run."""

    def __init__(self, local_clock, sleep_windows):
        """Creates new PumpScheduler instance.

        Args:
            local_clock: A local clock interface
            sleep_windows: A list of 2-tuples, each representing a sleep window.
                Tuple items are datetime.time objects.
        """
        self._local_clock = local_clock
        self._sleep_windows = sleep_windows

    def is_running_pump_allowed(self):
        """Returns True if OK to run pump, otherwise False.

        Pump is not allowed to run from the start of a sleep window (inclusive)
        to the end of a sleep window (exclusive).
        """
        current_time = self._local_clock.now().time()

        for sleep_time, wake_time in self._sleep_windows:
            # Check if sleep window wraps midnight.
            if wake_time < sleep_time:
                if current_time >= sleep_time or current_time < wake_time:
                    return False
            else:
                if sleep_time <= current_time < wake_time:
                    return False

        return True