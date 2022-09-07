import unittest
from pprint import pprint

from src.parser import Parser
from parameterized import parameterized


class ParserTests(unittest.TestCase):
    @parameterized.expand([
        ["binary expression", "2 + 2;", [{
            'type': 'ExpressionStatement',
            'expression': {
                'type': 'BinaryExpression',
                'operator': '+',
                'left': {
                    'type': 'NumericLiteral',
                    'value': 2
                },
                'right': {
                    'type': 'NumericLiteral',
                    'value': 2
                }
            }
        }]],

        # left: 3 + 2
        # right: 2
        ["nested binary expression", "3 + 2 - 2;", [{
            'type': 'ExpressionStatement',
            'expression': {
                'type': 'BinaryExpression',
                'operator': '-',
                'left': {
                    'type': 'BinaryExpression',
                    'operator': '+',
                    'left': {
                        'type': 'NumericLiteral',
                        'value': 3
                    },
                    'right': {
                        'type': 'NumericLiteral',
                        'value': 2
                    },
                },
                'right': {
                    'type': 'NumericLiteral',
                    'value': 2
                },
            }
        }]],

        # left: 2
        # right: 2 * 3
        ["multiplication", "2 + 2 * 3;", [{
            'type': 'ExpressionStatement',
            'expression': {
                'type': 'BinaryExpression',
                'operator': '+',
                'left': {
                    'type': 'NumericLiteral',
                    'value': 2
                },
                'right': {
                    'type': 'BinaryExpression',
                    'operator': '*',
                    'left': {
                        'type': 'NumericLiteral',
                        'value': 2
                    },
                    'right': {
                        'type': 'NumericLiteral',
                        'value': 3
                    },
                },
            }
        }]],

        # left: 2 + 2
        # right: 3
        ["multiplication", "(2 + 2) * 3;", [{
            'type': 'ExpressionStatement',
            'expression': {
                'type': 'BinaryExpression',
                'operator': '*',
                'left': {
                    'type': 'BinaryExpression',
                    'operator': '+',
                    'left': {
                        'type': 'NumericLiteral',
                        'value': 2
                    },
                    'right': {
                        'type': 'NumericLiteral',
                        'value': 2
                    },
                },
                'right': {
                    'type': 'NumericLiteral',
                    'value': 3
                },
            }
        }]],
    ])
    def test_statement(self, name, program, expected):
        parser = Parser()
        out = parser.parse(program)
        self.assertEqual({'type': 'Program', 'body': expected}, out, f'Failed: {name}')
