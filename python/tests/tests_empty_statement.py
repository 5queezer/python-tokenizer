import unittest
from pprint import pprint

from src.parser import Parser
from parameterized import parameterized


class ParserTests(unittest.TestCase):
    @parameterized.expand([
        ["emtpy statement", ";", [{
            'type': 'EmptyStatement'
        }]],
    ])
    def test_statement(self, name, program, expected):
        parser = Parser()
        out = parser.parse(program)
        self.assertEqual({'type': 'Program', 'body': expected}, out, f'Failed: {name}')
