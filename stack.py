from z3 import ArithRef
from utils import value_is_constant

class Stack():
    def __init__(self):
        self.stack = []

    def push(self, value):
        if value_is_constant(value) == True:
            value = value.rjust(32, b"\x00")
        self.stack.append(value)

    def pop(self):
        return self.stack.pop()

    def peek(self):
        return self.stack[-1]