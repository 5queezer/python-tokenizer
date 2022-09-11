import unittest
import yaml
import os


from src.parser import Parser
from parameterized import parameterized


class ParserTests(unittest.TestCase):
    yout = os.path.splitext(os.path.basename(__file__))[0].partition('_')[2] + '.yaml'
    file = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.file = open(cls.yout, 'w')

    @classmethod
    def tearDownClass(cls) -> None:
        cls.file.close()
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
        output = parser.parse(program)
        self.assertEqual({'type': 'Program', 'body': expected}, output, f'Failed: {name}')
        yaml.dump([{'name': name, 'input': program, 'output': output}], stream=self.file, sort_keys=False)