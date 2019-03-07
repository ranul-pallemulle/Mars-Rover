import unittest
from coreutils import parser

class TestParser(unittest.TestCase):
    def test_parse(self):
        with self.assertRaises(parser.CommandError):
            result = parser.parse(" ") # can't have leading white space
        with self.assertRaises(parser.CommandError):
            result = parser.parse('') # can't have empty command
        with self.assertRaises(parser.CommandError):
            result = parser.parse(" Hey I am") # leading spaces
        with self.assertRaises(parser.CommandError):
            result = parser.parse("Hey I am ") # trailing spaces
        with self.assertRaises(parser.CommandError):
            result = parser.parse("Hey  I") # too many spaces
        with self.assertRaises(parser.CommandError):
            result = parser.parse("Hey I am Groot") # max 3 words
        with self.assertRaises(parser.CommandError):
            result = parser.parse("START_JOYSTICK arg1 arg2 arg3") # too many
        with self.assertRaises(parser.CommandError): # 
            result = parser.parse("Hey I am") # isn't an actual command
        result = parser.parse("START_JOYSTICK arg1 arg2")
        self.assertEqual(parser.CommandTypes.START_JOYSTICK, result[0])
        self.assertEqual('arg1', result[1])
        self.assertEqual('arg2', result[2])
        result = parser.parse("STOP_JOYSTICK")
        self.assertEqual(parser.CommandTypes.STOP_JOYSTICK, result[0])
