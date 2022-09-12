from src.tokenizer import Tokenizer, TokenType as T, Token


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
          | ClassDeclaration
          ;
        """
        match self._lookahead.type:
            case T.SEMI:
                return self.empty_statement()
            case T.LBRACE:
                return self.block_statement()
            case T.LET:
                return self.variable_statement()
            case T.DEF:
                return self.function_declaration()
            case T.CLASS:
                return self.class_declaration()
            case T.RETURN:
                return self.return_statement()
            case T.IF:
                return self.if_statement()
            case T.WHILE | T.DO | T.FOR:
                return self.iteration_statement()
            case _:
                return self.expression_statement()

    def class_declaration(self) -> dict:
        """
        ClassDeclaration
          : 'class' Identifier OptClassExtends BlockStatement
          ;
        """
        self._eat(T.CLASS)
        id = self.identifier()
        super_class = self.class_extends() if self._lookahead.type == T.EXTENDS else None
        body = self.block_statement()
        return {
            'type': 'ClassDeclaration',
            'id': id,
            'superClass': super_class,
            'body': body
        }

    def class_extends(self) -> dict:
        """
        ClassExtends
          : 'extends' Identifier
          ;
        """
        self._eat(T.EXTENDS)
        return self.identifier()

    def function_declaration(self):
        """
        FunctionDeclaration
          : 'def' Identifier '(' OptFormalParameterList ')' BlockStatement
          ;
        """
        self._eat(T.DEF)
        name = self.identifier()
        self._eat(T.LPAR)
        params = self.formal_parameter_list() if self._lookahead.type != T.RPAR else []
        self._eat(T.RPAR)
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
            if self._lookahead.type != T.COMMA:
                break
            self._eat(T.COMMA)

        return params

    def return_statement(self):
        """
        ReturnStatement
          : 'return' OptExpression ';'
          ;
        """
        self._eat(T.RETURN)
        argument = self.expression() if self._lookahead.type != T.SEMI else None
        self._eat(T.SEMI)
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
            case T.WHILE:
                return self.while_statement()
            case T.DO:
                return self.do_while_statement()
            case T.FOR:
                return self.for_statement()

    def while_statement(self) -> dict:
        """
        WhileStatement
         : 'while' '(' Expression ')' Statement
         ;
        """
        self._eat(T.WHILE)
        self._eat(T.LPAR)
        test = self.expression()
        self._eat(T.RPAR)

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
        self._eat(T.DO)
        body = self.statement()
        self._eat(T.WHILE)
        self._eat(T.LPAR)
        test = self.expression()
        self._eat(T.RPAR)
        self._eat(T.SEMI)

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
        self._eat(T.FOR)
        self._eat(T.LPAR)

        init = self.for_statement_init() if self._lookahead.type != T.SEMI else None
        self._eat(T.SEMI)

        test = self.expression() if self._lookahead.type != T.SEMI else None
        self._eat(T.SEMI)

        update = self.expression() if self._lookahead.type != T.RPAR else None
        self._eat(T.RPAR)

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
        if self._lookahead.type == T.LET:
            return self.variable_statement_init()
        return self.expression()

    def if_statement(self):
        """
        IfStatement
          : 'if' '(' Expression ')' Statement
          | 'if' '(' Expression ')' Statement 'else' Statement
          ;
        """
        self._eat(T.IF)
        self._eat(T.LPAR)
        test = self.expression()
        self._eat(T.RPAR)
        consequent = self.statement()

        alternate = self._eat(T.ELSE) and self.statement() \
            if self._lookahead is not None and self._lookahead.type == T.ELSE \
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
        self._eat(T.LET)
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
        self._eat(T.SEMI)
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
            if self._lookahead.type == T.COMMA:
                self._eat(T.COMMA)
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
        if self._lookahead.type != T.SEMI and self._lookahead.type != T.COMMA:
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
        self._eat(T.SIMPLE_ASSIGN)
        return self.assignment_expression()

    def empty_statement(self) -> dict:
        self._eat(T.SEMI)
        return {
            'type': 'EmptyStatement'
        }

    def block_statement(self) -> dict:
        """
        BlockStatement
          : '{' OptStatementList '}'
        """
        self._eat(T.LBRACE)
        body = self.statement_list(T.RBRACE) if self._lookahead.type != T.RBRACE else []
        self._eat(T.RBRACE)
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
        self._eat(T.SEMI)
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
            T.ADDITIVE_OPERATOR
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
            T.MULTIPLICATIVE_OPERATOR
        )

    def _logical_expression(self, builder_name, operator_token: T) -> dict:
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

    def _binary_expression(self, builder_name, operator_token: T) -> dict:
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
        if self._lookahead.type == T.ADDITIVE_OPERATOR:
            operator = self._eat(T.ADDITIVE_OPERATOR).value
        elif self._lookahead.type == T.NOT:
            operator = self._eat(T.NOT).value
        if operator is not None:
            return {
                'type': 'UnaryExpression',
                'operator': operator,
                'argument': self.unary_expression()  # --x
            }
        return self.left_hand_side_expression()

    def primary_expression(self) -> dict:
        """
        PrimaryExpression
          : Literal
          | ParanthesizedExpression
          | Identifier
          | ThisExpression
          | NewExpression
          ;
        """
        if self._is_literal(self._lookahead.type):
            return self.literal()
        match self._lookahead.type:
            case T.LPAR:
                return self.paranthesized_expression()
            case T.IDENTIFIER:
                return self.identifier()
            case T.THIS:
                return self.this_expression()
            case T.NEW:
                return self.new_expression()
            case _:
                return self.left_hand_side_expression()

    def new_expression(self):
        """
        NewExpression
          : 'new' MemberExpression Arguments
          ;
        """
        self._eat(T.NEW)
        return {
            'type': 'NewExpression',
            'callee': self.member_expression(),
            'arguments': self.arguments()
        }

    def this_expression(self) -> dict:
        """
        ThisExpression
          : 'this'
          ;
        """
        self._eat(T.THIS)
        return {
            'type': 'ThisExpression'
        }

    def super(self) -> dict:
        """
        Super
          : 'super'
          ;
        """
        self._eat(T.SUPER)
        return {
            'type': 'Super'
        }

    @staticmethod
    def _is_literal(token_type: T) -> bool:
        return token_type in [T.NUMBER, T.STRING, T.TRUE, T.FALSE, T.NULL]

    def paranthesized_expression(self) -> dict:
        """
        ParanthesizedExpression
          : T.LPAR Expression ')'
          ;
        """
        self._eat(T.LPAR)
        expression = self.expression()
        self._eat(T.RPAR)
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
          : CallMemberExpression
          ;
        """
        return self.call_member_expression()

    def call_member_expression(self):
        """
        CallMemberExpression
          : MemberExpression
          | CallExpression
          ;
        """
        if self._lookahead.type == T.SUPER:
            return self._call_expression(self.super())

        member = self.member_expression()

        if self._lookahead.type == T.LPAR:
            return self._call_expression(member)
        return member

    def _call_expression(self, callee):
        """
        Generic call expression helper.

        CallExpression
          : Callee Arguments
          ;

        Callee
          : MemberExpression
          | Super
          | CallExpression
          ;
        """
        call_expression = {
            'type': 'CallExpression',
            'callee': callee,
            'arguments': self.arguments()
        }

        if self._lookahead.type == T.LPAR:
            call_expression = self._call_expression(call_expression)

        return call_expression

    def arguments(self):
        """
        Arguments
          : '(' OptArgumentList ')'
          ;
        """
        self._eat(T.LPAR)
        argument_list = self.argument_list() if self._lookahead.type != T.RPAR else []
        self._eat(T.RPAR)
        return argument_list

    def argument_list(self) -> list:
        """
        ArgumentList
          : AssignmentExpression
          | ArgumentList ',' AssignmentExpression
          ;
        """
        argument_list = [self.assignment_expression()]
        while self._lookahead.type == T.COMMA and self._eat(T.COMMA):
            argument_list.append(self.assignment_expression())

        return argument_list

    def member_expression(self):
        """
        MemberExpression
          : PrimaryExpression
          | MemberExpression '.' Identifier
          | MemberExpression '[' Expression ']'
          ;
        """

        _object = self.primary_expression()
        while self._lookahead.type == T.DOT or self._lookahead.type == T.LSQB:
            if self._lookahead.type == T.DOT:
                self._eat(T.DOT)
                _property = self.identifier()
                _object = {
                    'type': 'MemberExpression',
                    'computed': False,
                    'object': _object,
                    'property': _property
                }

            if self._lookahead.type == T.LSQB:
                self._eat(T.LSQB)
                _property = self.expression()
                self._eat(T.RSQB)
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
        name = self._eat(T.IDENTIFIER).value
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
        return token_type in [T.SIMPLE_ASSIGN, T.COMPLEX_ASSIGN]

    def assignment_operator(self) -> Token:
        """
        AssignmentOperator
          : SIMPLE_ASSIGN
          | COMPLEX_ASSIGN
          ;
        """
        if self._lookahead.type == T.SIMPLE_ASSIGN:
            return self._eat(T.SIMPLE_ASSIGN)
        return self._eat(T.COMPLEX_ASSIGN)

    def logical_OR_expression(self):
        """
        Logical OR expression.
        
        x || y
        
        LogicalORExpression
          : LogicalANDExpression OR LogicalORExpression
          | LogicalORExpression
          ;
        """
        return self._logical_expression('logical_AND_expression', T.OR)

    def logical_AND_expression(self):
        """
        Logical AND expression.

        x && y

        LogicalANDExpression
          : EqualityExpression AND LogicalANDExpression
          | LogicalANDExpression
          ;
        """
        return self._logical_expression('equality_expression', T.AND)

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
        return self._binary_expression('relational_expression', T.EQUALITY_OPERATOR)

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
        return self._binary_expression('additive_expression', T.RELATIONAL_OPERATOR)

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
            case T.NUMBER:
                return self.numeric_literal()
            case T.STRING:
                return self.string_literal()
            case T.TRUE:
                return self.boolean_literal(True)
            case T.FALSE:
                return self.boolean_literal(False)
            case T.NULL:
                return self.null_literal()

        raise SyntaxError('Literal: unexpected literal production')

    def boolean_literal(self, value):
        """
        BooleanLiteral
          : 'true'
          | 'false'
          ;
        """
        self._eat(T.TRUE if value else T.FALSE)
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
        self._eat(T.NULL)
        return {
            'type': 'NullLiteral',
            'value': None
        }

    def string_literal(self) -> dict:
        """
        StringLiteral
        """
        token = self._eat(T.STRING)
        return {
            'type': 'StringLiteral',
            'value': token.value[1:-1]
        }

    def numeric_literal(self) -> dict:
        """
        NumericLiteral
        """
        token = self._eat(T.NUMBER)
        return {
            'type': 'NumericLiteral',
            'value': int(token.value)
        }

    def _eat(self, token_type: T) -> Token:
        token = self._lookahead
        if token is None:
            raise SyntaxError(f'Unexpected end of input, expected: {token_type}')
        if token_type != token.type:
            raise SyntaxError(f'Unexpected token: {token.value}, expected {token_type}')
        self._lookahead = self._tokenizer.get_next_token()
        return token
