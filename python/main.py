from pprint import pprint
import sys

from src.parser import Parser

if __name__ == '__main__':
    parser = Parser()
    out = parser.parse('(2);')
    pprint(out)