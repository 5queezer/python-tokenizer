import unittest
from pprint import pprint

from src.parser import Parser
from parameterized import parameterized


class ParserTests(unittest.TestCase):
    @parameterized.expand([
        ["simple variable declaration", "let x = 42;", [{
            'type': 'VariableStatement',
            'declarations': [
                {
                    'type': 'VariableDeclaration',
                    'id': {
                        'type': 'Identifier',
                        'name': 'x'
                    },
                    'init': {
                        'type': 'NumericLiteral',
                        'value': 42
                    }
                }
            ]
        }]],

        ['Multiple variable declarations, no init', 'let x, y;', [{
                'type': 'VariableStatement',
                'declarations': [
                    {
                        'type': 'VariableDeclaration',
                        'id': {
                            'type': 'Identifier',
                            'name': 'x',
                        },
                        'init': None,
                    },
                    {
                        'type': 'VariableDeclaration',
                        'id': {
                            'type': 'Identifier',
                            'name': 'y',
                        },
                        'init': None,
                    },
                ],
        }]],

        ['Multiple variable declarations', 'let x, y = 42;', [{
                'type': 'VariableStatement',
                'declarations': [
                    {
                        'type': 'VariableDeclaration',
                        'id': {
                            'type': 'Identifier',
                            'name': 'x',
                        },
                        'init': None,
                    },
                    {
                        'type': 'VariableDeclaration',
                        'id': {
                            'type': 'Identifier',
                            'name': 'y',
                        },
                        'init': {
                            'type': 'NumericLiteral',
                            'value': 42,
                        },
                    },
                ]
        }]]
    ])
    def test_statement(self, name, program, expected):
        parser = Parser()
        out = parser.parse(program)
        self.assertEqual({'type': 'Program', 'body': expected}, out, f'Failed: {name}')
