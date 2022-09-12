import yaml
import json
import sys
from argparse import ArgumentParser, Namespace
from src.parser import Parser

def arguments() -> Namespace:
    p = ArgumentParser(description='Parse letter files.')
    p.add_argument('-e', '--expression', help='parse expression')
    p.add_argument('-f', '--file', help='parse file')
    p.add_argument('--format', help='output format', default='yaml', choices=['yaml', 'json'])
    args = p.parse_args()
    return args

def dumper(format, ast):
    if format == 'yaml':
        return yaml.dump(ast, sort_keys=False)
    else:
        return json.dumps(ast, indent=2, sort_keys=False)
def main():
    args = arguments()
    if args.expression:
        expression = args.expression
    elif args.file:
        with open(args.file) as file:
            expression = file.read()
    else:
        expression = sys.stdin.read()

    parser = Parser()
    ast = parser.parse(expression)
    out = dumper(args.format, ast)
    print(out)


if __name__ == '__main__':
    main()
