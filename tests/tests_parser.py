import unittest
from src.parser import Parser


class ParserTests(unittest.TestCase):
    def test_number(self):
        program = '42'
        parser = Parser()
        out = parser.parse(program)
        self.assertEqual({'type': 'Program', 'body': {'type': 'NumericLiteral', 'value': 42}}, out)

    def test_string_double_quote(self):
        program = '"hello"'
        parser = Parser()
        out = parser.parse(program)
        self.assertEqual({'type': 'Program', 'body': {'type': 'StringLiteral', 'value': 'hello'}}, out)

    def test_string_single_quote(self):
        program = "'hello'"
        parser = Parser()
        out = parser.parse(program)
        self.assertEqual({'type': 'Program', 'body': {'type': 'StringLiteral', 'value': 'hello'}}, out)

    def test_whitespace(self):
        program = "   42 "
        parser = Parser()
        out = parser.parse(program)
        self.assertEqual({'type': 'Program', 'body': {'type': 'NumericLiteral', 'value': 42}}, out)

