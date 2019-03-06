import unittest
from unittest.mock import patch, Mock
import coreutils.configure as cfg

class TestConfigure(unittest.TestCase):

    def setUp(self):
        self.testconf = cfg.OverallConfiguration("RaspiCode/tests/testsettings.xml")
        self.testMotorConf = cfg.MotorConfiguration("RaspiCode/tests/testsettings.xml")
        self.testCameraConf = cfg.CameraConfiguration("RaspiCode/tests/testsettings.xml")
        
    def test_make_searchstr_valid(self):
        req_list = ["{Motors}[nonexit]Fake.{Motor}[name]Left"]
        res = self.testconf._make_searchstr_list(req_list)
        expect = ["./MOTORS[@NONEXIT='Fake']/MOTOR[@NAME='Left']"]
        self.assertEqual(res, expect)

    def test_provide_settings_valid_correct(self):
        req_list = ["{Motors}[name]Wheels.{Motor}[name]Right"]
        tempstr = self.testconf._make_searchstr_list(req_list)
        tempstr_expect = ["./MOTORS[@NAME='Wheels']/MOTOR[@NAME='Right']"]
        self.assertEqual(tempstr, tempstr_expect)
        res = self.testconf.provide_settings(req_list)
        self.assertIsNotNone(res)

    def test_provide_settings_valid_wrong(self):
        req_list = ["{Motors}[nonexit]Fake.{Motor}[name]Left"]
        res = self.testconf.provide_settings(req_list)
        self.assertIsNone(res)
        
    def test_provide_settings_invalid(self):
        req_list = ["{Motors}[Fake.{Motors}[Left]"] # invalid
        res = self.testconf.provide_settings(req_list)
        self.assertIsNone(res)

    def test_getsubelemvalue_valid(self):
        req_list = ["{Motors}[name]Wheels.{Motor}[name]Right"]
        res0 = self.testconf.provide_settings(req_list)
        res = self.testconf._getsubelemvalue(res0[0], "TYPE", "PWM")
        self.assertIsNotNone(res)

    def test_getsubelemvalue_invalid(self):
        req_list = ["{Motors}[name]Wheels.{Motor}[name]Right"]
        res0 = self.testconf.provide_settings(req_list)
        res = self.testconf._getsubelemvalue(res0[0], "FAKE", "PWM")
        self.assertIsNone(res)
        
    def test_top_level_element_value_valid(self):
        name = "sometopelem"
        val = self.testconf.top_level_element_value(name)
        self.assertEqual(val, "0.2")
        name = "someOTHERtopelem"
        val = self.testconf.top_level_element_value(name)
        self.assertEqual(val, "0.5")

    def test_top_level_element_value_invalid(self):
        name = "nonexistent"
        val = self.testconf.top_level_element_value(name)
        self.assertIsNone(val)

    def test_motor_get_pwm_pin(self):
        motor_group = "Arm"
        motor_name = "Servo2"
        pin_num = self.testMotorConf.get_pwm_pin(motor_group, motor_name)
        self.assertTrue(isinstance(pin_num, int))
        self.assertEqual(pin_num, 23)

    def test_motor_get_pwm_pin_badval(self):
        motor_group = "Arm"
        motor_name = "Servo3"
        with self.assertRaises(cfg.ConfigurationError):
            pin_num = self.testMotorConf.get_pwm_pin(motor_group, motor_name)

    def test_motor_get_digital_pin(self):
        motor_group = "Arm"
        motor_name = "Servo2"
        pin_num = self.testMotorConf.get_digital_pin(motor_group,motor_name)
        self.assertTrue(isinstance(pin_num, int))
        self.assertEqual(pin_num, 7)

    # def test_hardware_mode(self):
    #     mode = self.testconf.hardware_mode()
    #     self.assertEqual(mode, "LAPTOP")

    def test_opmodes_directories(self):
        mode = self.testconf.opmodes_directories()
        self.assertEqual(mode, ['joystick', 'robotic_arm'])

    def test_resources_directories(self):
        resource = self.testconf.resources_directories()
        self.assertEqual(resource, ['resources/mock_motors.py'])

    def test_camera_capture_framerate(self):
        framerate = self.testCameraConf.capture_framerate()
        self.assertTrue(isinstance(framerate,int))
        self.assertEqual(framerate, 60)

    def test_camera_capture_frame_width(self):
        frame_width = self.testCameraConf.capture_frame_width()
        self.assertTrue(isinstance(frame_width,int))
        self.assertEqual(frame_width, 200)

    def test_camera_capture_frame_height(self):
        frame_height = self.testCameraConf.capture_frame_height()
        self.assertTrue(isinstance(frame_height,int))
        self.assertEqual(frame_height, 150)

    def test_camera_stream_port(self):
        port = self.testCameraConf.stream_port()
        self.assertTrue(isinstance(port, int))
        self.assertEqual(port, 5564)

    def test_camera_stream_framerate(self):
        framerate = self.testCameraConf.stream_framerate()
        self.assertTrue(isinstance(framerate, int))
        self.assertEqual(framerate, 30)

    def test_camera_stream_frame_width(self):
        frame_width = self.testCameraConf.stream_frame_width()
        self.assertTrue(isinstance(frame_width, int))
        self.assertEqual(frame_width, 640)

    def test_camera_stream_frame_height(self):
        frame_height = self.testCameraConf.stream_frame_height()
        self.assertTrue(isinstance(frame_height, int))
        self.assertEqual(frame_height, 480)
        
