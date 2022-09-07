import unittest
from pprint import pprint

from src.parser import Parser
from parameterized import parameterized


class ParserTests(unittest.TestCase):
    @parameterized.expand([
        ["number", "42;", [{
            'type': 'ExpressionStatement',
            'expression': {
                'type': 'NumericLiteral',
                'value': 42
            }
        }]],

        ["string double quote", '"hello";', [{
            'type': 'ExpressionStatement',
            'expression': {
                'type': 'StringLiteral',
                'value': 'hello'
            }
        }]],

        ["string single quote", "'hello';", [{
            'type': 'ExpressionStatement',
            'expression': {
                'type': 'StringLiteral',
                'value': 'hello'
            }
        }]],

        ["whitespace", "   42; ", [{
            'type': 'ExpressionStatement',
            'expression': {
                'type': 'NumericLiteral',
                'value': 42
            }
        }]],

        ["single line comment", """
        // Number: 42
        42;
        
        """, [{
            'type': 'ExpressionStatement',
            'expression': {
                'type': 'NumericLiteral',
                'value': 42
            }
        }]],

        ["multi line comment", """
            /**
             * Documentation comment:
             */
             
            "hello";
            
            """, [{
            'type': 'ExpressionStatement',
            'expression': {
                'type': 'StringLiteral',
                'value': 'hello'
            }
        }]],

    ])
    def test_expression_statement(self, name, program, expected):

        parser = Parser()
        out = parser.parse(program)
        self.assertEqual({'type': 'Program', 'body': expected},  out, f'Failed: {name}')


