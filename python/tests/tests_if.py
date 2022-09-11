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
        ["if else statement", """
        
            if (x) {
                x = 1;
            } else {
                x = 2;
            }
            
        """,
         [{
             'type': 'IfStatement',
             'test': {
                 'type': 'Identifier',
                 'name': 'x',
             },
             'consequent': {
                 'type': 'BlockStatement',
                 'body': [
                     {
                         'type': 'ExpressionStatement',
                         'expression': {
                             'type': 'AssignmentExpression',
                             'operator': '=',
                             'left': {
                                 'type': 'Identifier',
                                 'name': 'x',
                             },
                             'right': {
                                 'type': 'NumericLiteral',
                                 'value': 1,
                             },
                         },
                     },
                 ],
             },
             'alternate': {
                 'type': 'BlockStatement',
                 'body': [
                     {
                         'type': 'ExpressionStatement',
                         'expression': {
                             'type': 'AssignmentExpression',
                             'operator': '=',
                             'left': {
                                 'type': 'Identifier',
                                 'name': 'x',
                             },
                             'right': {
                                 'type': 'NumericLiteral',
                                 'value': 2,
                             },
                         },
                     },
                 ],
             },

         }]
         ],

        ['No else part', """
        
            if (x) {
              x = 1;
            }
    
        """,
         [{
             'type': 'IfStatement',
             'test': {
                 'type': 'Identifier',
                 'name': 'x',
             },
             'consequent': {
                 'type': 'BlockStatement',
                 'body': [
                     {
                         'type': 'ExpressionStatement',
                         'expression': {
                             'type': 'AssignmentExpression',
                             'operator': '=',
                             'left': {
                                 'type': 'Identifier',
                                 'name': 'x',
                             },
                             'right': {
                                 'type': 'NumericLiteral',
                                 'value': 1,
                             },
                         },
                     },
                 ],
             },
             'alternate': None,
         }]
         ],
    ])
    def test_statement(self, name, program, expected):
        parser = Parser()
        output = parser.parse(program)
        self.assertEqual({'type': 'Program', 'body': expected}, output, f'Failed: {name}')
        yaml.dump([{'name': name, 'input': program, 'output': output}], stream=self.file, sort_keys=False)
