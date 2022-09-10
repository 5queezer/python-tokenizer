from src.tokenizer import Tokenizer, TokenType, Token


class Parser:

    def __init__(self):
        self._string: str = ''
        self._tokenizer: Tokenizer or None = None
        self._lookahead: Token or None = None

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
        while self._lookahead is not None and self._lookahead.type != stop_lookahead:
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
        if self._lookahead.type == TokenType.SEMICOLON:
            return self.empty_statement()
        elif self._lookahead.type == TokenType.OPEN_SQBRACKET:
            return self.block_statement()
        return self.expression_statement()

    def empty_statement(self) -> dict:
        self._eat(TokenType.SEMICOLON)
        return {
            'type': 'EmptyStatement'
        }

    def block_statement(self) -> dict:
        """
        BlockStatement
          : '{' OptStatementList TokenType.CLOSE_SQBRACKET
        """
        self._eat(TokenType.OPEN_SQBRACKET)
        body = self.statement_list(TokenType.CLOSE_SQBRACKET) if self._lookahead.type != TokenType.CLOSE_SQBRACKET else []
        self._eat(TokenType.CLOSE_SQBRACKET)
        return {
            'type': 'BlockStatement',
            'body': body
        }

    def expression_statement(self) -> dict:
        """
        Statement
          : ExpressionStatement
          ;
        """
        expression = self.expression()
        self._eat(TokenType.SEMICOLON)
        return {
            'type': 'ExpressionStatement',
            'expression': expression
        }

    def additive_expression(self) -> dict:
        """
        AdditiveExpression
          : Literal
          | MultiplicativeExpression
          | AdditiveExpression ADDITIVE_OPERATOR Literal -> Literal ADDITIVE_OPERATOR Literal ADDITIVE_OPERATOR Literal
          ;
        """
        return self._binary_expression(
            'multiplicative_expression',
            TokenType.ADDITIVE_OPERATOR
        )

    def multiplicative_expression(self) -> dict:
        """
        MultiplicativeExpression
          : PrimaryExpression
          | MultiplicativeExpression MULTIPLICATIVE_OPERATOR PrimaryExpression -> PrimaryExpression MULTIPLICATIVE_OPERATOR
          ;
        """
        return self._binary_expression(
            'primary_expression',
            TokenType.MULTIPLICATIVE_OPERATOR
        )

    def _binary_expression(self, builder_name, operator_token: TokenType) -> dict:
        """
        Generic binary expression
        """
        left = getattr(self, builder_name)()

        # operator: +, -
        while self._lookahead.type == operator_token:
            operator = self._eat(operator_token).value
            right = getattr(self, builder_name)()
            left = {
                'type': 'BinaryExpression',
                'operator': operator,
                'left': left,
                'right': right
            }
        return left

    def primary_expression(self) -> dict:
        """
        PrimaryExpression
          : Literal
          | ParanthesizedExpression
          | LeftHandSideExpression
          ;
        """
        if self._is_literal(self._lookahead.type):
            return self.literal()
        if self._lookahead.type == TokenType.OPEN_BRACKET:
            return self.paranthesized_expression()
        return self.left_hand_side_expression()

    def _is_literal(self, token_type: TokenType) -> bool:
        return token_type in [TokenType.NUMBER, TokenType.STRING]

    def paranthesized_expression(self) -> dict:
        """
        ParanthesizedExpression
          : TokenType.OPEN_BRACKET Expression ')'
          ;
        """
        self._eat(TokenType.OPEN_BRACKET)
        expression = self.expression()
        self._eat(TokenType.CLOSE_BRACKET)
        return expression

    def expression(self) -> dict:
        """
        Expression
          : Literal
          ;
        """
        return self.assignment_expression()

    def assignment_expression(self) -> dict:
        """
        AssignmentExpression
          : AdditiveExpression
          | LeftHandSideExpression AssignmentOperator AssignmentExpression
          ;
        """
        left = self.additive_expression()
        if not self._is_assignment_operator(self._lookahead.type):
            return left
        return {
            'type': 'AssignmentExpression',
            'operator': self.assignment_operator().value,
            'left': self._check_valid_assignment_target(left),
            'right': self.assignment_expression()
        }

    def left_hand_side_expression(self):
        """
        LeftHandSideExpression
          : Identifier
          ;
        """
        return self.identifier()

    def identifier(self):
        """
        Identifier
          : IDENTIFIER
          ;
        """
        name = self._eat(TokenType.IDENTIFIER).value
        return {
            'type': 'Identifier',
            'name': name
        }

    @staticmethod
    def _check_valid_assignment_target(node):
        """
        Extra check whether it's a valid assignment target
        """
        if node['type'] == 'Identifier':
            return node
        raise SyntaxError('Invalid left-hand side in assignment expression')

    @staticmethod
    def _is_assignment_operator(token_type) -> bool:
        return token_type in [TokenType.SIMPLE_ASSIGN, TokenType.COMPLEX_ASSIGN]

    def assignment_operator(self) -> Token:
        if self._lookahead.type == TokenType.SIMPLE_ASSIGN:
            return self._eat(TokenType.SIMPLE_ASSIGN)
        return self._eat(TokenType.COMPLEX_ASSIGN)

    def literal(self) -> dict:
        """
        Literal
          : NumericLiteral
          | StringLiteral
          ;
        """
        # lookahead = self._lookahead()
        if self._lookahead.type == TokenType.NUMBER:
            return self.numeric_literal()
        elif self._lookahead.type == TokenType.STRING:
            return self.string_literal()
        raise SyntaxError('Literal: unexpected literal production')

    def string_literal(self) -> dict:
        """
        StringLiteral
        """
        token = self._eat(TokenType.STRING)
        return {
            'type': 'StringLiteral',
            'value': token.value[1:-1]
        }

    def numeric_literal(self) -> dict:
        """
        NumericLiteral
        """
        token = self._eat(TokenType.NUMBER)
        return {
            'type': 'NumericLiteral',
            'value': int(token.value)
        }

    def _eat(self, token_type: TokenType) -> Token:
        token = self._lookahead
        if token is None:
            raise SyntaxError(f'Unexpected end of input, expected: {token_type}')
        if token_type != token.type:
            raise SyntaxError(f'Unexpected token: {token.value}, expected {token_type}')
        self._lookahead = self._tokenizer.get_next_token()
        return token
