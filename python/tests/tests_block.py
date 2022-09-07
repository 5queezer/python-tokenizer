import unittest
from pprint import pprint

from src.parser import Parser
from parameterized import parameterized


class ParserTests(unittest.TestCase):
    @parameterized.expand([
        ["block", """
        {
            42;
            'hello';
        }
        """, [{
            'type': 'BlockStatement',
            'body': [{
                'type': 'ExpressionStatement',
                'expression': {
                    'type': 'NumericLiteral',
                    'value': 42
                }
            }, {
                'type': 'ExpressionStatement',
                'expression': {
                    'type': 'StringLiteral',
                    'value': 'hello'
                }
            }]}
        ]],

        ["empty block", """
        {

        }
        """, [{
            'type': 'BlockStatement',
            'body': []}
        ]],

        ["nested block", """
        {
            42;
            {
                'hello';
            }
        }
        """, [{
            'type': 'BlockStatement',
            'body': [{
                'type': 'ExpressionStatement',
                'expression': {
                    'type': 'NumericLiteral',
                    'value': 42
                }
            }, {
                'type': 'BlockStatement',
                'body': [{
                    'type': 'ExpressionStatement',
                    'expression': {
                        'type': 'StringLiteral',
                        'value': 'hello'
                    }
                }]}
            ]}
        ]],
    ])
    def test_statement(self, name, program, expected):
        parser = Parser()
        out = parser.parse(program)
        self.assertEqual({'type': 'Program', 'body': expected}, out, f'Failed: {name}')
