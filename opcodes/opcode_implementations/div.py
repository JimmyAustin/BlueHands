from ..opcode import Opcode
from utils import int_to_bytes, bytes_to_int, value_is_constant
from z3 import UDiv


class DivOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        val1 = machine.stack.pop()
        val2 = machine.stack.pop()

        if value_is_constant(val1):
            val1 = bytes_to_int(val1)
            if value_is_constant(val2):
                val2 = bytes_to_int(val2)
                machine.stack.push(int_to_bytes(val1 // val2))
            else:
                machine.stack.push(UDiv(val1, val2))
        else:
            if value_is_constant(val2):
                val2 = bytes_to_int(val2)
                machine.stack.push(UDiv(val1, val2))
            else:
                machine.stack.push(UDiv(val1, val2))
