import contextlib
import datetime
import os
import unittest

import mock
import pytz

from greenpithumb import camera_manager


class TestCameraManager(unittest.TestCase):

    @mock.patch.object(os.path, 'exists')
    @mock.patch.object(os, 'makedirs')
    def test_save_photo(self, mock_makedirs, mock_exists):
        image_path = 'C:/Users/Jeet/'
        mock_local_clock = mock.Mock()
        mock_camera = mock.Mock()
        mock_exists.return_value = True
        mock_local_clock.now.return_value = datetime.datetime(
            2016, 7, 23, 10, 51, 9, 928000, tzinfo=pytz.utc)
        with contextlib.closing(
                camera_manager.CameraManager(image_path, mock_local_clock,
                                             mock_camera)) as manager:
            manager.save_photo()
        mock_camera.capture.assert_called_once_with(
            'C:/Users/Jeet/2016-07-23T10-51-09.928000+00-00.jpg')
        mock_exists.assert_called_once_with(image_path)
        mock_makedirs.assert_not_called()
        mock_camera.close.assert_called()

    @mock.patch.object(os.path, 'exists')
    @mock.patch.object(os, 'makedirs')
    def test_create_path_if_does_not_exist(self, mock_makedirs, mock_exists):
        image_path = 'C:/Users/Jeet/'
        mock_local_clock = mock.Mock()
        mock_camera = mock.Mock()
        mock_exists.return_value = False
        with contextlib.closing(
                camera_manager.CameraManager(image_path, mock_local_clock,
                                             mock_camera)):
            pass
        mock_exists.assert_called_once_with(image_path)
        mock_makedirs.assert_called_once_with(image_path)
