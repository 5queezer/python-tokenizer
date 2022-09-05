import unittest
from src.parser import Parser


class ParserTests(unittest.TestCase):
    def test_number(self):
        program = '42'
        parser = Parser()
        out = parser.parse(program)
        self.assertEqual({'type': 'Program', 'body': {'type': 'NumericLiteral', 'value': 42}}, out)

    def test_string(self):
        program = '"hello"'
        parser = Parser()
        out = parser.parse(program)
        self.assertEqual({'type': 'Program', 'body': {'type': 'StringLiteral', 'value': 'hello'}}, out)

