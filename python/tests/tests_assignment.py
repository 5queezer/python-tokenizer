import unittest
from pprint import pprint

from src.parser import Parser
from parameterized import parameterized


class ParserTests(unittest.TestCase):
    @parameterized.expand([
        ["simple assignment", "x = 42;", [{
            'type': 'ExpressionStatement',
            'expression': {
                'type': 'AssignmentExpression',
                'operator': '=',
                'left': {
                    'type': 'Identifier',
                    'name': 'x'
                },
                'right': {
                    'type': 'NumericLiteral',
                    'value': 42
                }
            }
        }]],

        ["chained assignment", "x = y = 42;", [{
            'type': 'ExpressionStatement',
            'expression': {
                'type': 'AssignmentExpression',
                'operator': '=',
                'left': {
                    'type': 'Identifier',
                    'name': 'x'
                },
                'right': {
                    'type': 'AssignmentExpression',
                    'operator': '=',
                    'left': {
                        'type': 'Identifier',
                        'name': 'y'
                    },
                    'right': {
                        'type': 'NumericLiteral',
                        'value': 42
                    }
                }
            }
        }]],
    ])
    def test_statement(self, name, program, expected):
        parser = Parser()
        out = parser.parse(program)
        self.assertEqual({'type': 'Program', 'body': expected}, out, f'Failed: {name}')
