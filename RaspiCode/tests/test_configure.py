import unittest
from unittest.mock import patch, Mock
import coreutils.configure as cfg

class TestConfigure(unittest.TestCase):

    def setUp(self):
        self.testconf = cfg.OverallConfiguration("tests/testsettings.xml")
        self.testMotorConf = cfg.MotorConfiguration("tests/testsettings.xml")
        
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

    def test_hardware_mode(self):
        mode = self.testconf.hardware_mode()
        self.assertEqual(mode, "LAPTOP")

    def test_opmodes_directories(self):
        mode = self.testconf.opmodes_directories()
        self.assertEqual(mode, ['joystick', 'robotic_arm'])

    def test_resources_directories(self):
        resource = self.testconf.resources_directories()
        self.assertEqual(resource, ['resources/mock_motors.py'])
