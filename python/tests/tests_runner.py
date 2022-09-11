import sys
import unittest
import yaml
import glob

from parameterized import parameterized

from src.parser import Parser

tests = []
for file in glob.glob('*.yaml'):
    with open(file, "r") as stream:
        try:
            contents = yaml.safe_load(stream)
            tests.extend(list(map(lambda x: [f"{file:30s} | {x['name']}", x['input'], x['output']], contents)))
        except yaml.YAMLError as exc:
            print(exc, file=sys.stderr)
            exit(1)


class RunnerTests(unittest.TestCase):

    def setUp(self) -> None:
        self.parser = Parser()

    @parameterized.expand(tests)
    def test_run(self, name, inp, expected):
        print('❌', name, end='')
        try:
            output = self.parser.parse(inp)
            self.assertEqual(expected, output, msg=f'Error in {name}')
            print('\r✅', name)
        except Exception as ex:
            print()
            raise ex


