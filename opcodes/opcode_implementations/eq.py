from ..opcode import Opcode
from z3 import If
from utils import int_to_bytes, bytes_to_int, value_is_constant, bv1, bv0


class EqOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        val1 = machine.stack.pop()
        val2 = machine.stack.pop()

        if value_is_constant(val1):
            val1 = bytes_to_int(val1)
            if value_is_constant(val2):
                val2 = bytes_to_int(val2)
                value = 1 if val1 == val2 else 0
                machine.stack.push(int_to_bytes(value))
            else:
                machine.stack.push(If(val1 == val2, bv1, bv0))
        else:
            if value_is_constant(val2):
                val2 = bytes_to_int(val2)
                machine.stack.push(If(val1 == val2, bv1, bv0))
            else:
                machine.stack.push(If(val1 == val2, bv1, bv0))
