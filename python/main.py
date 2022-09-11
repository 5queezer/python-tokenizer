import yaml
import json
from src.parser import Parser

if __name__ == '__main__':
    parser = Parser()
    input = '''
    for (;;) {
    
    }
    '''
    output = parser.parse(input)
    test = {
        'input': input,
        'output': output
    }
    print(yaml.dump(test, sort_keys=False))
    # print(json.dumps(test, indent=2))

