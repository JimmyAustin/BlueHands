from ..opcode import Opcode
from utils import int_to_bytes, bytes_to_int

class EqOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        val1 = bytes_to_int(machine.stack.pop())
        val2 = bytes_to_int(machine.stack.pop())
        value = 1 if val1 == val2 else 0
        machine.stack.push(int_to_bytes(value))
