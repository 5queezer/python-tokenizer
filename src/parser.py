from src.tokenizer import Tokenizer


class Parser:
    def __init__(self):
        self._lookahead = None
        self._string = None
        self._tokenizer = None

    def parse(self, string):
        self._string = string
        self._tokenizer = Tokenizer(string)
        self._lookahead = self._tokenizer.get_next_token()
        return self.program()

    def program(self):
        return {
            'type': 'Program',
            'body': self.numeric_literal()
        }

    def numeric_literal(self):
        token = self._eat('NUMBER')
        return {
            'type': 'NumericLiteral',
            'value': int(self._string)
        }

    def _eat(self, token_type):
        token = self._lookahead
        if token is None:
            raise SyntaxError(f'Unexpected end of input, expected: {token_type}')
        if token_type != token['type']:
            raise SyntaxError(f'Unexpected token: {token["value"]}, expected {token_type}')
