import yaml
import json
from src.parser import Parser

if __name__ == '__main__':
    parser = Parser()
    input = '''
    let s = "Hello, world";
    let i = 0;
    
    while (i < s.length) {
        s[i];
        // console.log(i, s[i]);
        i += 1;
    }

    '''
    output = parser.parse(input)
    test = {
        'input': input,
        'output': output
    }
    print(input)
    print(yaml.dump(output, sort_keys=False))
    # print(json.dumps(test, indent=2))

