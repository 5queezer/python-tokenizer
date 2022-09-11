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
          | IterationStatement
          | FunctionDeclaration
          | ReturnStatement
          ;
        """
        match self._lookahead.type:
            case t.SEMI:
                return self.empty_statement()
            case t.LBRACE:
                return self.block_statement()
            case t.LET:
                return self.variable_statement()
            case t.DEF:
                return self.function_declaration()
            case t.RETURN:
                return self.return_statement()
            case t.IF:
                return self.if_statement()
            case t.WHILE | t.DO | t.FOR:
                return self.iteration_statement()
            case _:
                return self.expression_statement()

    def function_declaration(self):
        """
        FunctionDeclaration
          : 'def' Identifier '(' OptFormalParameterList ')' BlockStatement
          ;
        """
        self._eat(t.DEF)
        name = self.identifier()
        self._eat(t.LPAR)
        params = self.formal_parameter_list() if self._lookahead.type != t.RPAR else []
        self._eat(t.RPAR)
        body = self.block_statement()
        return {
            'type': 'FunctionDeclaration',
            'name': name,
            'params': params,
            'body': body
        }

    def formal_parameter_list(self):
        """
        FormalParameterList
            : Identifier
            | FormalParameterList ',' Identifier
            ;
        """
        params = []

        while True:
            params.append(self.identifier())
            if self._lookahead.type != t.COMMA:
                break
            self._eat(t.COMMA)

        return params

    def return_statement(self):
        """
        ReturnStatement
          : 'return' OptExpression ';'
          ;
        """
        self._eat(t.RETURN)
        argument = self.expression() if self._lookahead.type != t.SEMI else None
        self._eat(t.SEMI)
        return {
            'type': 'ReturnStatement',
            'argument': argument
        }


    def iteration_statement(self):
        """
        IterationStatement
          : WhileStatement
          | DoWhileStatement
          | ForStatement
          ;
        """
        match self._lookahead.type:
            case t.WHILE:
                return self.while_statement()
            case t.DO:
                return self.do_while_statement()
            case t.FOR:
                return self.for_statement()

    def while_statement(self) -> dict:
        """
        WhileStatement
         : 'while' '(' Expression ')' Statement
         ;
        """
        self._eat(t.WHILE)
        self._eat(t.LPAR)
        test = self.expression()
        self._eat(t.RPAR)

        body = self.statement()
        return {
            'type': 'WhileStatement',
            'test': test,
            'body': body
        }

    def do_while_statement(self) -> dict:
        """
        DoWhileStatement
         : 'do' Statement 'while' '(' Expression ')' ';'
         ;
        """
        self._eat(t.DO)
        body = self.statement()
        self._eat(t.WHILE)
        self._eat(t.LPAR)
        test = self.expression()
        self._eat(t.RPAR)
        self._eat(t.SEMI)

        return {
            'type': 'DoWhileStatement',
            'test': test,
            'body': body
        }
    
    def for_statement(self):
        """
        ForStatement
          : 'for' '(' OptForStatementInit ';' OptExpression ';' OptExpression ')' Statement
          ;
        """
        self._eat(t.FOR)
        self._eat(t.LPAR)

        init = self.for_statement_init() if self._lookahead.type != t.SEMI else None
        self._eat(t.SEMI)

        test = self.expression() if self._lookahead.type != t.SEMI else None
        self._eat(t.SEMI)

        update = self.expression() if self._lookahead.type != t.RPAR else None
        self._eat(t.RPAR)

        body = self.statement()

        return {
            'type': 'ForStatement',
            'init': init,
            'test': test,
            'update': update,
            'body': body
        }

    def for_statement_init(self):
        """
        ForStatementInit
          : VariableStatementInit
          | Expression
          ;
        """
        if self._lookahead.type == t.LET:
            return self.variable_statement_init()
        return self.expression()

    def if_statement(self):
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

    def variable_statement_init(self):
        """
        VariableStatementInit
          : 'let' VariableDeclarationList
          ;
        """
        self._eat(t.LET)
        declarations = self.variable_declaration_list()
        return {
            'type': 'VariableStatement',
            'declarations': declarations
        }

    def variable_statement(self) -> dict:
        """
        VariableStatement
          : 'VariableDeclarationInit ';'
          ;
        """
        variable_statement = self.variable_statement_init()
        self._eat(t.SEMI)
        return variable_statement

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
          : UnaryExpression
          | MultiplicativeExpression MULTIPLICATIVE_OPERATOR UnaryExpression
          ;
        """
        return self._binary_expression(
            'unary_expression',
            t.MULTIPLICATIVE_OPERATOR
        )

    def _logical_expression(self, builder_name, operator_token: t) -> dict:
        """
        Generic helper for LogicalExpression nodes
        """
        left = getattr(self, builder_name)()

        # operator: +, -
        while self._lookahead.type == operator_token:
            operator = self._eat(operator_token).value
            right = getattr(self, builder_name)()
            left = {
                'type': 'LogicalExpression',
                'operator': operator,
                'left': left,
                'right': right
            }
        return left

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


    def unary_expression(self) -> dict:
        """
        UnaryExpression
            : LeftHandSideExpression
            | ADDITIVE_OPERATOR UnaryExpression
            | LOGICAL_NOT UnaryExpression
            ;
        """
        operator = None
        if self._lookahead.type == t.ADDITIVE_OPERATOR:
            operator = self._eat(t.ADDITIVE_OPERATOR).value
        elif self._lookahead.type == t.NOT:
            operator = self._eat(t.NOT).value
        if operator is not None:
            return {
                'type': 'UnaryExpression',
                'operator': operator,
                'argument': self.unary_expression() # --x
            }
        return self.left_hand_side_expression()


    def primary_expression(self) -> dict:
        """
        PrimaryExpression
          : Literal
          | ParanthesizedExpression
          | Identifier
          ;
        """
        if self._is_literal(self._lookahead.type):
            return self.literal()
        match self._lookahead.type:
            case t.LPAR:
                return self.paranthesized_expression()
            case t.IDENTIFIER:
                return self.identifier()
            case _:
                return self.left_hand_side_expression()

    @staticmethod
    def _is_literal(token_type: t) -> bool:
        return token_type in [t.NUMBER, t.STRING, t.TRUE, t.FALSE, t.NULL]

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
          : LogicalORExpression
          | LeftHandSideExpression AssignmentOperator AssignmentExpression
          ;
        """
        left = self.logical_OR_expression()
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
          : MemberExpression
          ;
        """
        return self.member_expression()

    def member_expression(self):
        """
        MemberExpression
          : PrimaryExpression
          | MemberExpression '.' Identifier
          | MemberExpression '[' Expression ']'
          ;
        """

        _object = self.primary_expression()
        while self._lookahead.type == t.DOT or self._lookahead.type == t.LSQB:
            # MemberExpression '.' Identifier
            if self._lookahead.type == t.DOT:
                self._eat(t.DOT)
                _property = self.identifier()
                _object = {
                    'type': 'MemberExpression',
                    'computed': False,
                    'object': _object,
                    'property': _property
                }

            if self._lookahead.type == t.LSQB:
                self._eat(t.LSQB)
                _property = self.expression()
                self._eat(t.RSQB)
                _object = {
                    'type': 'MemberExpression',
                    'computed': True,
                    'object': _object,
                    'property': _property
                }
        return _object

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
        if node['type'] == 'Identifier' or node['type'] == 'MemberExpression':
            return node
        raise SyntaxError('Invalid left-hand side in assignment expression')

    @staticmethod
    def _is_assignment_operator(token_type) -> bool:
        return token_type in [t.SIMPLE_ASSIGN, t.COMPLEX_ASSIGN]

    def assignment_operator(self) -> Token:
        """
        AssignmentOperator
          : SIMPLE_ASSIGN
          | COMPLEX_ASSIGN
          ;
        """
        if self._lookahead.type == t.SIMPLE_ASSIGN:
            return self._eat(t.SIMPLE_ASSIGN)
        return self._eat(t.COMPLEX_ASSIGN)

    def logical_OR_expression(self):
        """
        Logical OR expression.
        
        x || y
        
        LogicalORExpression
          : LogicalANDExpression OR LogicalORExpression
          | LogicalORExpression
          ;
        """
        return self._logical_expression('logical_AND_expression', t.OR)

    def logical_AND_expression(self):
        """
        Logical AND expression.

        x && y

        LogicalANDExpression
          : EqualityExpression AND LogicalANDExpression
          | LogicalANDExpression
          ;
        """
        return self._logical_expression('equality_expression', t.AND)
    
    def equality_expression(self):
        """
        EQUALITY_OPERATOR: ==, !=

          x == y
          x != y

        EqualityExpression
          : RelationalExpression
          | EqualityExpression EQUALITY_OPERATOR RelationalExpression
          ;
        """
        return self._binary_expression('relational_expression', t.EQUALITY_OPERATOR)

    def relational_expression(self):
        """
        RELATIONAL_OPERATOR: >, >=, <, <=
       
          x > y
          x >= y
          x < y
          x <= y
       
        RelationalExpression
          : AdditiveExpression
          | AdditiveExpression RELATIONAL_OPERATOR RelationalExpression
          ;
        """
        return self._binary_expression('additive_expression', t.RELATIONAL_OPERATOR)

    def literal(self) -> dict:
        """
        Literal
          : NumericLiteral
          | StringLiteral
          | BooleanLiteral
          | NullLiteral
          ;
        """
        match self._lookahead.type:
            case t.NUMBER:
                return self.numeric_literal()
            case t.STRING:
                return self.string_literal()
            case t.TRUE:
                return self.boolean_literal(True)
            case t.FALSE:
                return self.boolean_literal(False)
            case t.NULL:
                return self.null_literal()

        raise SyntaxError('Literal: unexpected literal production')

    def boolean_literal(self, value):
        """
        BooleanLiteral
          : 'true'
          | 'false'
          ;
        """
        self._eat(t.TRUE if value else t.FALSE)
        return {
          'type': 'BooleanLiteral',
          'value': value
        }

    def null_literal(self):
        """
        NullLiteral
          : 'null'
          ;
        """
        self._eat(t.NULL)
        return {
          'type': 'NullLiteral',
          'value': None
        }

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
