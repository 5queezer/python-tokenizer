
class Tokenizer:
    def __init__(self, string):
        self._string = string
        self._cursor = 0

    def has_more_tokens(self):
        return self._cursor < len(self._string)

    def get_next_token(self):
        if not self.has_more_tokens():
            return None
        string = self._string[self._cursor:]

        if string[0].isdigit():
            number = ''
            while self._cursor < len(string) and string[self._cursor].isdigit():
                number += string[self._cursor]
                self._cursor += 1

            return {
                'type': 'NUMBER',
                'value': number
            }
        return None
