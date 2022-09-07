import re

# Tokenizer spec.
spec = [
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
    [r"^'[^']*'", 'STRING'],
    [r'^"[^"]*"', 'STRING'],

    # ----------------------------
    # Symbols, delimiters
    [r'^;', ';'],
    [r'^{', '{'],
    [r'^}', '}'],

    # ----------------------------
    # Math operators
    [r'^[+\-]', 'ADDITIVE_OPERATOR'],

    # ----------------------------
    # Numbers
    [r'^\d+', 'NUMBER'],
]


class Tokenizer:
    def __init__(self, string):
        self._string: str = string
        self._cursor: int = 0

    def has_more_tokens(self) -> bool:
        return self._cursor < len(self._string)

    def get_next_token(self) -> dict or None:
        if not self.has_more_tokens():
            return None
        string = self._string[self._cursor:]

        for regexp, token_type in spec:
            token_value = self._match(regexp, string)
            if token_value is None:
                continue
            if token_type is None:
                return self.get_next_token()
            return {
                'type': token_type,
                'value': token_value
            }
        raise SyntaxError(f'Unexpected token: "{string[0]}"')

    def _match(self, regexp, string) -> str or None:
        matched = re.match(regexp, string)
        if not matched:
            return None
        self._cursor += len(matched.group(0))
        return matched.group(0)
