import contextlib
import datetime
import unittest

import mock
import pytz

from greenpithumb import camera_manager


class TestCameraManager(unittest.TestCase):

    def test_save_photo(self):
        folder_path = 'C:/Users/Jeet/'
        mock_local_clock = mock.Mock()
        mock_camera = mock.Mock()
        mock_local_clock.now.return_value = datetime.datetime(
            2016, 7, 23, 10, 51, 9, 928000, tzinfo=pytz.utc)
        with contextlib.closing(
                camera_manager.CameraManager(folder_path, mock_local_clock,
                                             mock_camera)) as manager:
            manager.save_photo()
            mock_camera.capture.assert_called_once_with(
                'C:/Users/Jeet/2016-07-23T10-51-09.928000+00-00.jpg')
        mock_camera.close.assert_called()
