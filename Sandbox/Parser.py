class Parser:
    def __init__(self, data):
        self.data = data
        self.index = 0
        self.len = len(self.data)

    def __nonzero__(self):
        return self.index < self.len

    def peek(self):
        if self:
            return self.data[self.index]

    def isdigit(self):
        if self and self.data[self.index] in '0123456789':
            return True
        else:
            return False

    def pop(self):
        if self:
            self.index += 1
            return self.data[self.index-1]

    def parse_whitespace(self):
        while self.peek() in (' ', '\f', '\n', '\r', '\t'):
            self.pop()

    def parse_comma(self):
        self.parse_whitespace()
        if self.peek() == ',':
            self.pop()
            self.parse_whitespace()

    def parse_number(self):
        output = ""
        if self.peek() in ('+', '-'):
            output += self.pop()
        while self.isdigit():
            output += self.pop()
        if self.peek() == '.':
            output += self.pop()
            while self.isdigit():
                output += self.pop()
        if self.peek() in ('e', 'E'):
            output += self.pop()
            if self.peek() in ('+', '-'):
                output += self.pop()
            while self.isdigit():
                output += self.pop()
        if output:
            return float(output)

    def parse_flag(self):
        if self.peek() in ('0', '1'):
            return self.pop()

    def parse_word(self):
        output = ""
        while self.peek().isalpha():
            output += self.pop()
        return output
