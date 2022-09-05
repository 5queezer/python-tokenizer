import re

# Tokenizer spec.
spec = [
    # Whitespace
    [r'^\s+', None],
    # Numbers
    [r'^\d+', 'NUMBER'],
    # Strings
    [r"^'[^']*'", 'STRING'],
    [r'^"[^"]*"', 'STRING'],
]


class Tokenizer:
    def __init__(self, string):
        self._string = string
        self._cursor = 0

    def is_EOF(self):
        return self._cursor == len(self._string)

    def has_more_tokens(self):
        return self._cursor < len(self._string)

    def get_next_token(self):
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
        raise SyntaxError(f'Unexpected token {string[0]}')

    def _match(self, regexp, string):
        matched = re.match(regexp, string)
        if not matched:
            return None
        self._cursor += len(matched.group(0))
        return matched.string
