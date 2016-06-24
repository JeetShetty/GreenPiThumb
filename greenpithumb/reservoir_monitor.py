class ReservoirMonitor(object):
    """Monitors and returns alerts about a GreenPiThumb system's reservoir"""

    def __init__(self, reservoir):
        """Creates a new ReservoirMonitor instance.

        Args:
            reservoir: Reservoir interface.
        """
        self._reservoir = reservoir

    def _alert_water_level_low(self):
        """Alerts user if the reservoir should to be refilled."""
        raise NotImplementedError()
