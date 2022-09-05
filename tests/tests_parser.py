import unittest
from src.parser import Parser


class ParserTests(unittest.TestCase):
    def test_number(self):
        program = '42'
        parser = Parser()
        out = parser.parse(program)
        self.assertEqual(out, {'type': 'Program', 'body': {'type': 'NumericLiteral', 'value': 42}})

