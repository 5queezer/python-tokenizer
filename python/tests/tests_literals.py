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
        output = parser.parse(program)
        self.assertEqual({'type': 'Program', 'body': expected},  output, f'Failed: {name}')
        yaml.dump([{'name': name, 'input': program, 'output': output}], stream=self.file, sort_keys=False)


