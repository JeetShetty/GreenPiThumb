class Error(Exception):
    pass


class ReservoirUnderWeightError(Error):
    pass


class Reservoir(object):
    """Provides information about a water reservoir."""

    def __init__(self, weight_sensor, container_weight):
        """Creates a new Reservoir instance.

        Args:
            weight_sensor: Weight sensor interface.
            container_weight: Reservoir container weight in grams.
        """
        self._weight_sensor = weight_sensor
        self._container_weight = container_weight

    def reservoir_level(self):
        """Returns reservoir level in ml.

        Raises:
            ReservoirUnderWeightError: Reservoir weight is less than that of
                the empty container.
        """
        reservoir_weight_grams = self._weight_sensor.weight()
        if reservoir_weight_grams < self._container_weight:
            raise ReservoirUnderWeightError(
                ('Unexpected weight measured for reservoir (%.1f g), as it is '
                 'less than the weight of an empty reservoir (%.1f g).') % (
                     reservoir_weight_grams, self._container_weight))

        water_weight_grams = reservoir_weight_grams - self._container_weight
        return water_weight_grams  #1 gr water ~ 1 ml water
