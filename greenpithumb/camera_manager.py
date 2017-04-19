import logging
import os

logger = logging.getLogger(__name__)

# Format of filename to write for camera image file (assumes timestamp is in
# UTC), as YYYY-MM-DDTHH:MMZ (minutes-level precision).
_FILENAME_FORMAT = '%Y-%m-%dT%H%MZ.jpg'
# Light level below which camera will not capture photos.
LIGHT_THRESHOLD_PCT = 60


class CameraManager(object):
    """Captures and saves photos to the filesystem."""

    def __init__(self, image_path, clock, camera, light_sensor):
        """Creates a new camera manager instance.

        Args:
            image_path: Path name of the folder where images will be stored.
            clock: Clock interface.
            camera: Camera interface.
            light_sensor: An interface for reading the light level.
        """
        if not os.path.exists(image_path):
            os.makedirs(image_path)
        self._image_path = image_path
        self._clock = clock
        self._camera = camera
        self._light_sensor = light_sensor

    def sufficient_light(self):
        """Checks if there is sufficient light to capture a photo.

        Returns:
            A boolean indicating whether or not there is sufficient light.
        """
        if self._light_sensor.light() >= LIGHT_THRESHOLD_PCT:
            return True
        return False

    def save_photo(self):
        """Captures an image from the camera and saves it to the filesystem."""
        path = os.path.join(self._image_path,
                            self._clock.now().strftime(_FILENAME_FORMAT))
        self._camera.capture(path)
        logger.info('saved new photo to %s', path)

    def close(self):
        """Closes the camera.

        Should be called when use of the camera is complete.
        """
        self._camera.close()
