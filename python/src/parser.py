from src.tokenizer import Tokenizer


class Parser:

    def __init__(self):
        self._string: str = ''
        self._tokenizer: Tokenizer or None = None
        self._lookahead: dict or None = None

    def parse(self, string) -> dict:
        self._string = string
        self._tokenizer = Tokenizer(string)
        self._lookahead = self._tokenizer.get_next_token()
        return self.program()

    def program(self) -> dict:
        return {
            'type': 'Program',
            'body': self.statement_list()
        }

    def literal(self) -> dict:
        # lookahead = self._lookahead()
        if self._lookahead['type'] == 'NUMBER':
            return self.numeric_literal()
        elif self._lookahead['type'] == 'STRING':
            return self.string_literal()
        raise SyntaxError('Literal: unexpected literal production')

    def string_literal(self) -> dict:
        token = self._eat('STRING')
        return {
            'type': 'StringLiteral',
            'value': token['value'][1:-1]
        }

    def numeric_literal(self) -> dict:
        token = self._eat('NUMBER')
        return {
            'type': 'NumericLiteral',
            'value': int(token['value'])
        }

    def _eat(self, token_type) -> dict:
        token = self._lookahead
        if token is None:
            raise SyntaxError(f'Unexpected end of input, expected: {token_type}')
        if token_type != token['type']:
            raise SyntaxError(f'Unexpected token: {token["value"]}, expected {token_type}')
        self._lookahead = self._tokenizer.get_next_token()
        return token
