from os import path


class CameraManager(object):
    """Captures and saves photos to the filesystem."""

    def __init__(self, folder_path, local_clock, camera):
        """Creates a new camera manager instance.

        Args:
            folder_path: Path name of the folder where pictures will be stored.
            local_clock: Local clock interface.
            camera: Camera interface.
        """
        self._folder_path = folder_path
        self._local_clock = local_clock
        self._camera = camera

    def save_photo(self):
        """Captures an image from the camera and saves it to the filesystem."""
        filename = self._local_clock.now().isoformat().replace(':', '-') + (
            '.jpg')
        self._camera.capture(path.join(self._folder_path, filename))

    def close(self):
        """Closes the camera.

        Should be called when use of the camera is complete.
        """
        self._camera.close()