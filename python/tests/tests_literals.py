import unittest
from src.parser import Parser
from parameterized import parameterized


class ParserTests(unittest.TestCase):
    @parameterized.expand([
        ["number", "42", {'type': 'NumericLiteral', 'value': 42}],
        ["string double quote", '"hello"', {'type': 'StringLiteral', 'value': 'hello'}],
        ["string single quote", "'hello'", {'type': 'StringLiteral', 'value': 'hello'}],
        ["whitespace", "   42 ", {'type': 'NumericLiteral', 'value': 42}],

        ["single line comment", """
        // Number: 42
        42
        
        """,
         {'type': 'NumericLiteral', 'value': 42}],

        ["multi line comment", """
            /**
             * Documentation comment:
             */
             
            "hello" 
            
            """,
         {'type': 'StringLiteral', 'value': 'hello'}],

    ])
    def test_literal(self, name, program, expected):

        parser = Parser()
        out = parser.parse(program)
        self.assertEqual({'type': 'Program', 'body': expected},  out, f'Failed: {name}')
