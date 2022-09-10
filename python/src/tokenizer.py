import re
from typing import NamedTuple
from enum import Enum, auto


class TokenType(Enum):
    STRING = auto()
    NUMBER = auto()
    IDENTIFIER = auto()
    SIMPLE_ASSIGN = auto()
    COMPLEX_ASSIGN = auto()
    ADDITIVE_OPERATOR = auto()
    MULTIPLICATIVE_OPERATOR = auto()
    SEMICOLON = auto()
    OPEN_SQBRACKET = auto()
    CLOSE_SQBRACKET = auto()
    OPEN_BRACKET = auto()
    CLOSE_BRACKET = auto()


class Token(NamedTuple):
    type: TokenType or None
    value: str


# Tokenizer spec.
spec: list[re.Pattern, TokenType or None] = [
    # Whitespace
    [r'^\s+', None],

    # ----------------------------
    # Comments

    # Skip single line-comments
    [r'^\/\/.*', None],

    # Skip multi line-comments
    [r'^\/\*[\s\S]*?\*\/', None],

    # ----------------------------
    # Strings
    [r"^'[^']*'", TokenType.STRING],
    [r'^"[^"]*"', TokenType.STRING],

    # ----------------------------
    # Symbols, delimiters
    [r'^;', TokenType.SEMICOLON],
    [r'^\{', TokenType.OPEN_SQBRACKET],
    [r'^\}', TokenType.CLOSE_SQBRACKET],
    [r'^\(', TokenType.OPEN_BRACKET],
    [r'^\)', TokenType.CLOSE_BRACKET],

    # ----------------------------
    # Numbers
    [r'^\d+', TokenType.NUMBER],

    # ----------------------------
    # Identifiers:
    [r'^[a-zA-Z_]\w*', TokenType.IDENTIFIER],

    # ----------------------------
    # Assignment operators =, *=, /=, +=, -=
    [r'^=', TokenType.SIMPLE_ASSIGN],
    [r'^[\*\/\+\-]=', TokenType.COMPLEX_ASSIGN],

    # ----------------------------
    # Math operators: +, -
    [r'^[+\-]', TokenType.ADDITIVE_OPERATOR],
    [r'^[*\/]', TokenType.MULTIPLICATIVE_OPERATOR],

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
        matched = re.match(regexp, string)
        if not matched:
            return None
        self._cursor += len(matched.group(0))
        return matched.group(0)
