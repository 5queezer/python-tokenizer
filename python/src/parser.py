from src.tokenizer import Tokenizer


class Parser:

    def __init__(self):
        self._string: str = ''
        self._tokenizer: Tokenizer or None = None
        self._lookahead: dict or None = None

    def parse(self, string) -> dict:
        """
        Main entry point
        Program
          : StatementList
          ;
        """
        self._string = string
        self._tokenizer = Tokenizer(string)
        self._lookahead = self._tokenizer.get_next_token()
        return self.program()

    def program(self) -> dict:
        return {
            'type': 'Program',
            'body': self.statement_list()
        }

    def statement_list(self, stop_lookahead=None) -> list:
        """
        StatementList
          : Statement
          | StatementList Statement -> Statement Statement Statement Statement
          ;
        """
        statement_list = [self.statement()]
        while self._lookahead is not None and self._lookahead['type'] != stop_lookahead:
            statement_list.append(self.statement())
        return statement_list

    def statement(self) -> dict:
        """
        Statement
          : ExpressionStatement
          | BlockStatement
          | EmptyStatement
          ;
        """
        if self._lookahead['type'] == ';':
            return self.empty_statement()
        elif self._lookahead['type'] == '{':
            return self.block_statement()
        else:
            return self.expression_statement()

    def empty_statement(self):
        self._eat(';')
        return {
            'type': 'EmptyStatement'
        }
    def block_statement(self) -> dict:
        """
        BlockStatement
          : '{' OptStatementList '}'
        """
        self._eat('{')
        body = self.statement_list('}') if self._lookahead['type'] != '}' else []
        self._eat('}')
        return {
            'type': 'BlockStatement',
            'body': body
        }

    def expression_statement(self):
        """
        Statement
          : ExpressionStatement
          ;
        """
        expression = self.expression()
        self._eat(';')
        return {
            'type': 'ExpressionStatement',
            'expression': expression
        }

    def expression(self):
        """
        Expression
          : Literal
          ;
        """
        return self.literal()

    def literal(self) -> dict:
        """
        Literal
          : NumericLiteral
          | StringLiteral
          ;
        """
        # lookahead = self._lookahead()
        if self._lookahead['type'] == 'NUMBER':
            return self.numeric_literal()
        elif self._lookahead['type'] == 'STRING':
            return self.string_literal()
        raise SyntaxError('Literal: unexpected literal production')

    def string_literal(self) -> dict:
        """
        StringLiteral
        """
        token = self._eat('STRING')
        return {
            'type': 'StringLiteral',
            'value': token['value'][1:-1]
        }

    def numeric_literal(self) -> dict:
        """
        NumericLiteral
        """
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
