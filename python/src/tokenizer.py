import re
from typing import NamedTuple
from enum import IntEnum, auto


class TokenType(IntEnum):
    STRING = auto()
    NUMBER = auto()
    IDENTIFIER = auto()
    SIMPLE_ASSIGN = auto()
    COMPLEX_ASSIGN = auto()
    ADDITIVE_OPERATOR = auto()
    MULTIPLICATIVE_OPERATOR = auto()
    RELATIONAL_OPERATOR = auto()
    EQUALITY_OPERATOR = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    SEMI = auto()
    LBRACE = auto()
    RBRACE = auto()
    LPAR = auto()
    RPAR = auto()
    LET = auto()
    IF = auto()
    ELSE = auto()
    TRUE = auto()
    FALSE = auto()
    NULL = auto()
    WHILE = auto()
    DO = auto()
    FOR = auto()
    DEF = auto()
    RETURN = auto()
    CLASS = auto()
    EXTENDS = auto()
    SUPER = auto()
    NEW = auto()
    THIS = auto()
    COMMA = auto()
    DOT = auto()

    LSQB = auto()
    RSQB = auto()


class Token(NamedTuple):
    type: TokenType or None
    value: str


# Tokenizer spec.
spec: list[tuple[re.Pattern, TokenType or None]] = [
    # Whitespace
    (r'\s+', None),

    # ----------------------------
    # Comments

    # Skip single line-comments
    (r'\/\/.*', None),

    # Skip multi line-comments
    (r'\/\*[\s\S]*?\*\/', None),

    # ----------------------------
    # Strings
    (r"'[^']*'", TokenType.STRING),
    (r'"[^"]*"', TokenType.STRING),

    # ----------------------------
    # Symbols, delimiters
    (r';', TokenType.SEMI),
    (r'\{', TokenType.LBRACE),
    (r'\}', TokenType.RBRACE),
    (r'\(', TokenType.LPAR),
    (r'\)', TokenType.RPAR),
    (r',', TokenType.COMMA),
    (r'\.', TokenType.DOT),
    (r'\[', TokenType.LSQB),
    (r'\]', TokenType.RSQB),

    # ----------------------------
    # Keywords
    (r'\blet\b', TokenType.LET),
    (r'\bif\b', TokenType.IF),
    (r'\belse\b', TokenType.ELSE),
    (r'\btrue\b', TokenType.TRUE),
    (r'\bfalse\b', TokenType.FALSE),
    (r'\bnull\b', TokenType.NULL),
    (r'\bwhile\b', TokenType.WHILE),
    (r'\bdo\b', TokenType.DO),
    (r'\bfor\b', TokenType.FOR),
    (r'\bdef\b', TokenType.DEF),
    (r'\breturn\b', TokenType.RETURN),
    (r'\bclass\b', TokenType.CLASS),
    (r'\bextends\b', TokenType.EXTENDS),
    (r'\bsuper\b', TokenType.SUPER),
    (r'\bnew\b', TokenType.NEW),
    (r'\bthis\b', TokenType.THIS),

    # ----------------------------
    # Numbers
    (r'\d+', TokenType.NUMBER),

    # ----------------------------
    # Identifiers:
    (r'[a-zA-Z_]\w*', TokenType.IDENTIFIER),

    # ----------------------------
    # Equality Operators: ==, !=
    (r'[=!]=', TokenType.EQUALITY_OPERATOR),

    # ----------------------------
    # Assignment operators =, *=, /=, +=, -=
    (r'=', TokenType.SIMPLE_ASSIGN),
    (r'[\*\/\+\-]=', TokenType.COMPLEX_ASSIGN),

    # ----------------------------
    # Relational Operators
    (r'[><]=?', TokenType.RELATIONAL_OPERATOR),

    # ----------------------------
    # Logical Operators: &&, ||
    (r'&&', TokenType.AND),
    (r'\|\|', TokenType.OR),
    (r'!', TokenType.NOT),

    # ----------------------------
    # Math operators: +, -
    (r'[+\-]', TokenType.ADDITIVE_OPERATOR),
    (r'[*\/]', TokenType.MULTIPLICATIVE_OPERATOR),

]


class Tokenizer:
    def __init__(self, string):
        self._string: str = string
        self._cursor: int = 0

    def has_more_tokens(self) -> bool:
        return self._cursor < len(self._string)

    def get_next_token(self) -> Token or None:
        if not self.has_more_tokens():
            return None
        string = self._string[self._cursor:]

        for regexp, token_type in spec:
            token_value = self._match(regexp, string)
            if token_value is None:
                continue
            if token_type is None:
                return self.get_next_token()
            return Token(type=token_type, value=token_value)
        raise SyntaxError(f'Unexpected token: "{string[0]}"')

    def _match(self, regexp, string) -> str or None:
        matched = re.match('^' + regexp, string)
        if not matched:
            return None
        self._cursor += len(matched.group(0))
        return matched.group(0)
