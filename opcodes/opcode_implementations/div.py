from ..opcode import Opcode
from utils import int_to_bytes, bytes_to_int


class DivOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        val1 = bytes_to_int(machine.stack.pop())
        val2 = bytes_to_int(machine.stack.pop())
        
        machine.stack.push(int_to_bytes(val1 // val2))
