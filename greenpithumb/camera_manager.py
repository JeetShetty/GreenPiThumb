import os


class CameraManager(object):
    """Captures and saves photos to the filesystem."""

    def __init__(self, image_path, local_clock, camera):
        """Creates a new camera manager instance.

        Args:
            image_path: Path name of the folder where images will be stored.
            local_clock: Local clock interface.
            camera: Camera interface.
        """
        if not os.path.exists(image_path):
            os.makedirs(image_path)
        self._image_path = image_path
        self._local_clock = local_clock
        self._camera = camera

    def save_photo(self):
        """Captures an image from the camera and saves it to the filesystem."""
        filename = self._local_clock.now().isoformat().replace(':', '-') + (
            '.jpg')
        self._camera.capture(os.path.join(self._image_path, filename))

    def close(self):
        """Closes the camera.

        Should be called when use of the camera is complete.
        """
        self._camera.close()