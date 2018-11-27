from ..opcode import Opcode
from utils import int_to_bytes, bytes_to_int


class ExpOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        val1 = int.from_bytes(machine.stack.pop(), 'big')
        val2 = int.from_bytes(machine.stack.pop(), 'big')
        
        machine.stack.push(int_to_bytes(val1 ** val2))
