from ..opcode import Opcode
from utils import bytes_to_int, int_to_bytes, value_is_constant, bv1, bv0
from z3 import If


class IszeroOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        value = machine.stack.pop()
        if value_is_constant(value):
            value = bytes_to_int(value)
            value_to_push = int_to_bytes(1 if value == 0 else 0)
        else:
            value_to_push = If(value == 0, bv1, bv0)

        machine.stack.push(value_to_push)
