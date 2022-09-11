import os
import sys
import unittest
import yaml
import glob
from parameterized import parameterized
from src.parser import Parser


def init() -> list:
    tests = []
    files = glob.glob('*.yaml')
    files.sort(key=os.path.getctime)
    for file in files:
        with open(file, "r") as stream:
            contents = yaml.safe_load(stream)
            tests.extend(list(map(lambda x: [f"{file:25s} | {x['name']}", x['input'], x['output']], contents)))
    return tests


class RunnerTests(unittest.TestCase):
    tests = init()

    def setUp(self) -> None:
        self.parser = Parser()

    @parameterized.expand(tests)
    def test_run(self, name, inp, expected):
        print('❌', name, end='', file=sys.stderr)
        try:
            output = self.parser.parse(inp)
            self.assertEqual(expected, output, msg=f'Error in {name}')
            print('\r✅', name, file=sys.stderr)
        except Exception as ex:
            print(file=sys.stderr)
            raise ex


