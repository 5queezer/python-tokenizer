import yaml
import json
from src.parser import Parser

if __name__ == '__main__':
    parser = Parser()
    out = parser.parse('''
    let x, y;
    ''')
    print(yaml.dump(out['body'], sort_keys=False))

