from src.tokenizer import Tokenizer, TokenType as t, Token
import tokenize


class Parser:

    def __init__(self):
        self._string: str = ''
        self._tokenizer: Tokenizer or None = None
        self._lookahead: Token or None = None

    def parse(self, string) -> dict:
        """
        Parses a string into an AST.
        """
        self._string = string
        self._tokenizer = Tokenizer(string)
        self._lookahead = self._tokenizer.get_next_token()
        return self.program()

    def program(self) -> dict:
        """
        # Main entry point.
        #
        # Program
        #   : StatementList
        #   ;
        """
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
          | VariableStatement
          | IfStatement
          ;
        """
        _type = self._lookahead.type
        if _type == t.SEMI:
            return self.empty_statement()
        elif _type == t.LBRACE:
            return self.block_statement()
        elif _type == t.LET:
            return self.variable_statement()
        elif _type == t.IF:
            return self.if_statememnt()
        else:
            return self.expression_statement()

    def if_statememnt(self):
        """
        IfStatement
          : 'if' '(' Expression ')' Statement
          | 'if' '(' Expression ')' Statement 'else' Statement
          ;
        """
        self._eat(t.IF)
        self._eat(t.LPAR)
        test = self.expression()
        self._eat(t.RPAR)
        consequent = self.statement()

        alternate = self._eat(t.ELSE) and self.statement() \
            if self._lookahead is not None and self._lookahead.type == t.ELSE \
            else None
        return {
            'type': 'IfStatement',
            'test': test,
            'consequent': consequent,
            'alternate': alternate
        }

    def variable_statement(self) -> dict:
        """
        VariableStatement
          : 'let' VariableDeclarationList
          ;
        """
        self._eat(t.LET)
        declarations = self.variable_declaration_list()
        self._eat(t.SEMI)
        return {
            'type': 'VariableStatement',
            'declarations': declarations
        }

    def variable_declaration_list(self):
        """
        VariableDeclarationList
          : VariableDeclaration
          | VariableDeclarationList ',' VariableDeclarationList
          ;
        """
        declarations = []
        while True:
            declarations.append(self.variable_declaration())
            if self._lookahead.type == t.COMMA:
                self._eat(t.COMMA)
            else:
                break
        return declarations

    def variable_declaration(self):
        """
        VariableDeclaration
          : Identifier OptVariableInitializer
          ;
        """
        _id = self.identifier()
        if self._lookahead.type != t.SEMI and self._lookahead.type != t.COMMA:
            init = self.variable_initializer()
        else:
            init = None
        return {
            'type': 'VariableDeclaration',
            'id': _id,
            'init': init
        }

    def variable_initializer(self):
        """
        VariableInitializer
          : SIMPLE_ASSIGN AssignmentExpression
          ;
        """
        self._eat(t.SIMPLE_ASSIGN)
        return self.assignment_expression()

    def empty_statement(self) -> dict:
        self._eat(t.SEMI)
        return {
            'type': 'EmptyStatement'
        }

    def block_statement(self) -> dict:
        """
        BlockStatement
          : '{' OptStatementList '}'
        """
        self._eat(t.LBRACE)
        body = self.statement_list(t.RBRACE) if self._lookahead.type != t.RBRACE else []
        self._eat(t.RBRACE)
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
        self._eat(t.SEMI)
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
            t.ADDITIVE_OPERATOR
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
            t.MULTIPLICATIVE_OPERATOR
        )

    def _binary_expression(self, builder_name, operator_token: t) -> dict:
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
        if self._lookahead.type == t.LPAR:
            return self.paranthesized_expression()
        return self.left_hand_side_expression()

    @staticmethod
    def _is_literal(token_type: t) -> bool:
        return token_type in [t.NUMBER, t.STRING]

    def paranthesized_expression(self) -> dict:
        """
        ParanthesizedExpression
          : t.LPAR Expression ')'
          ;
        """
        self._eat(t.LPAR)
        expression = self.expression()
        self._eat(t.RPAR)
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
        name = self._eat(t.IDENTIFIER).value
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
        return token_type in [t.SIMPLE_ASSIGN, t.COMPLEX_ASSIGN]

    def assignment_operator(self) -> Token:
        if self._lookahead.type == t.SIMPLE_ASSIGN:
            return self._eat(t.SIMPLE_ASSIGN)
        return self._eat(t.COMPLEX_ASSIGN)

    def literal(self) -> dict:
        """
        Literal
          : NumericLiteral
          | StringLiteral
          ;
        """
        # lookahead = self._lookahead()
        if self._lookahead.type == t.NUMBER:
            return self.numeric_literal()
        elif self._lookahead.type == t.STRING:
            return self.string_literal()
        raise SyntaxError('Literal: unexpected literal production')

    def string_literal(self) -> dict:
        """
        StringLiteral
        """
        token = self._eat(t.STRING)
        return {
            'type': 'StringLiteral',
            'value': token.value[1:-1]
        }

    def numeric_literal(self) -> dict:
        """
        NumericLiteral
        """
        token = self._eat(t.NUMBER)
        return {
            'type': 'NumericLiteral',
            'value': int(token.value)
        }

    def _eat(self, token_type: t) -> Token:
        token = self._lookahead
        if token is None:
            raise SyntaxError(f'Unexpected end of input, expected: {token_type}')
        if token_type != token.type:
            raise SyntaxError(f'Unexpected token: {token.value}, expected {token_type}')
        self._lookahead = self._tokenizer.get_next_token()
        return token
