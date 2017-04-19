import contextlib
import datetime
import os
import unittest

import mock
import pytz

from greenpithumb import camera_manager


class TestCameraManager(unittest.TestCase):

    def setUp(self):
        self.image_path = 'C:/Users/Jeet/'
        self.mock_local_clock = mock.Mock()
        self.mock_camera = mock.Mock()
        self.mock_light_sensor = mock.Mock()

    @mock.patch.object(os.path, 'exists')
    @mock.patch.object(os, 'makedirs')
    def test_save_photo(self, mock_makedirs, mock_exists):
        mock_exists.return_value = True
        self.mock_local_clock.now.return_value = datetime.datetime(
            2016, 7, 23, 10, 51, 9, 928000, tzinfo=pytz.utc)
        with contextlib.closing(
                camera_manager.CameraManager(
                    self.image_path, self.mock_local_clock, self.mock_camera,
                    self.mock_light_sensor)) as manager:
            manager.save_photo()
        self.mock_camera.capture.assert_called_once_with(
            'C:/Users/Jeet/2016-07-23T1051Z.jpg')
        mock_exists.assert_called_once_with(self.image_path)
        mock_makedirs.assert_not_called()
        self.mock_camera.close.assert_called()

    @mock.patch.object(os.path, 'exists')
    @mock.patch.object(os, 'makedirs')
    def test_create_path_if_does_not_exist(self, mock_makedirs, mock_exists):
        mock_exists.return_value = False
        with contextlib.closing(
                camera_manager.CameraManager(
                    self.image_path, self.mock_local_clock, self.mock_camera,
                    self.mock_light_sensor)):
            pass
        mock_exists.assert_called_once_with(self.image_path)
        mock_makedirs.assert_called_once_with(self.image_path)

    def test_sufficient_light_below_threshold(self):
        self.mock_light_sensor.light.return_value = (
            camera_manager.LIGHT_THRESHOLD_PCT - 1)
        with contextlib.closing(
                camera_manager.CameraManager(
                    self.image_path, self.mock_local_clock, self.mock_camera,
                    self.mock_light_sensor)) as manager:
            self.assertFalse(manager.sufficient_light())

    def test_sufficient_light_at_threshold(self):
        self.mock_light_sensor.light.return_value = (
            camera_manager.LIGHT_THRESHOLD_PCT)
        with contextlib.closing(
                camera_manager.CameraManager(
                    self.image_path, self.mock_local_clock, self.mock_camera,
                    self.mock_light_sensor)) as manager:
            self.assertTrue(manager.sufficient_light())

    def test_sufficient_light_above_threshold(self):
        self.mock_light_sensor.light.return_value = (
            camera_manager.LIGHT_THRESHOLD_PCT + 1)
        with contextlib.closing(
                camera_manager.CameraManager(
                    self.image_path, self.mock_local_clock, self.mock_camera,
                    self.mock_light_sensor)) as manager:
            self.assertTrue(manager.sufficient_light())
