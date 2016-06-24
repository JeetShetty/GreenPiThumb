import weight_sensor


class Reservoir(object):
    """Provides information about a GreenPiThumb system's water reservoir."""

    def __init__(self, weight_sensor, container_weight):
        """Creates a new Reservoir instance.

        Args:
            weight_sensor: Weight sensor interface.
            container_weight: Reservoir container weight in grams.
        """
        self._weight_sensor = weight_sensor
        self._container_weight = container_weight

    def reservoir_level(self):
        """Returns reservoir level in ml."""
        reservoir_weight_grams = self._weight_sensor.weight()
        water_weight_grams = reservoir_weight_grams - self._container_weight
        if water_weight_grams < weight_sensor.MIN_WEIGHT:
            raise ValueError('Water level out of range: %.1f' %
                             water_weight_grams)

        return water_weight_grams  #1 gr water ~ 1 ml water
