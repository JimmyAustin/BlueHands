class Stack():
    def __init__(self):
        self.stack = []

    def push(self, value):
        value = value.rjust(32, b"\x00")
        self.stack.append(value)

    def pop(self):
        return self.stack.pop()

    def peek(self):
        return self.stack[-1]