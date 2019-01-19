from utils import value_is_constant


class Stack():
    def __init__(self):
        self.stack = []

    def push(self, value):
        if value is None:
            import pdb; pdb.set_trace()
        if value_is_constant(value) is True:
            value = value.rjust(32, b"\x00")
        self.stack.append(value)

    def pop(self):
        return self.stack.pop()

    def peek(self):
        return self.stack[-1]
