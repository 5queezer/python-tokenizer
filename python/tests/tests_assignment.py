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
        output = parser.parse(program)
        self.assertEqual({'type': 'Program', 'body': expected}, output, f'Failed: {name}')
        yaml.dump([{'name': name, 'input': program, 'output': output}], stream=self.file, sort_keys=False)
