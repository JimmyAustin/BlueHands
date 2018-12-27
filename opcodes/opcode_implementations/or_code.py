from ..opcode import Opcode
from z3 import Or
from utils import int_to_bytes, value_is_constant, bytes_to_uint


class OrOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        val1 = machine.stack.pop()
        val2 = machine.stack.pop()

        if value_is_constant(val1):
            if value_is_constant(val2):
                machine.stack.push(bytes([x | y for x,y in zip(val1, val2)]))
            else:
                val1 = bytes_to_uint(val1)

                machine.stack.push(val1 | val2)
        else:
            if value_is_constant(val2):
                val2 = bytes_to_uint(val2)
                machine.stack.push(val1 | val2)
            else:
                machine.stack.push(val1 | val2)

def not_zero(value):
    for byte in value:
        if byte != 0:
            return True
    return False
