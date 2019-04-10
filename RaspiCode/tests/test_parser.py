import unittest
from unittest.mock import patch, Mock
from coreutils import parser
from enum import Enum

TestEnums = Enum('TestEnums',{'Joystick':1})

class TestParser(unittest.TestCase):
    @patch('coreutils.parser.gen_enum')
    def test_parse(self, mock_gen_enum):
        mock_gen_enum.return_value = TestEnums
        with self.assertRaises(parser.CommandError):
            result = parser.parse_entry(" ") # can't have leading white space
        with self.assertRaises(parser.CommandError):
            result = parser.parse_entry('') # can't have empty command
        with self.assertRaises(parser.CommandError):
            result = parser.parse_entry(" START_JOYSTICK 5560") # leading spaces
        with self.assertRaises(parser.CommandError):
            result = parser.parse_entry("START_JOYSTICK 5560 ") # trailing spaces
        with self.assertRaises(parser.CommandError):
            result = parser.parse_entry("START_JOYSTICK  5560") # too many spaces
        with self.assertRaises(parser.CommandError):
            result = parser.parse_entry("START_THING arg1 arg2 arg3") # no opmode 'Thing'
        with self.assertRaises(parser.CommandError): # 
            result = parser.parse_entry("Hey I am") # isn't an actual command
        result = parser.parse_entry("STOP_JOYSTICK")
        self.assertEqual(parser.CommandPrefixes.STOP, result[0])
        result = parser.parse_entry("STOP JOYSTICK")
        self.assertEqual(parser.CommandPrefixes.STOP, result[0])
        result = parser.parse_entry("START_JOYSTICK arg1 arg2")
        self.assertEqual(parser.CommandPrefixes.START, result[0])
        self.assertEqual('Joystick', result[1])
        self.assertEqual('arg1', result[2])
        self.assertEqual('arg2', result[3])
        result = parser.parse_entry("START JOYSTICK arg1 arg2")
        self.assertEqual(parser.CommandPrefixes.START, result[0])
        self.assertEqual('Joystick', result[1])
        self.assertEqual('arg1', result[2])
        self.assertEqual('arg2', result[3])        

        with self.assertRaises(parser.CommandError):
            result = parser.parse_entry("JOYSTICK hi") # invalid submode command format
        result = parser.parse_entry("JOYSTICK -> arg1 arg2")
        self.assertEqual(TestEnums.Joystick.name, result[0])
        self.assertEqual(result[1], 'arg1')
        self.assertEqual(result[2], 'arg2')
        with self.assertRaises(parser.CommandError):
            result = parser.parse_entry("JOYSTICK->arg1 arg2")

