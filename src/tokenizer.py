
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

        # Numbers
        if string[0].isdigit():
            number = ''
            while string[self._cursor].isdigit():
                number += string[self._cursor]
                self._cursor += 1
                if self.is_EOF():
                    break

            return {
                'type': 'NUMBER',
                'value': number
            }

        # Strings
        if string[0] == '"':
            s = ''
            while self._cursor < len(string):
                s += string[self._cursor]
                self._cursor += 1
                if string[self._cursor] == '"' or self.is_EOF():
                    break
            s += string[self._cursor]
            self._cursor += 1
            return {
                'type': 'STRING',
                'value': s
            }

        return None
