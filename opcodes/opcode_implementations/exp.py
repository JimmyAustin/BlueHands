from ..opcode import Opcode
from utils import uint_to_bytes, bytes_to_uint


class ExpOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        val1 = bytes_to_uint(machine.stack.pop())
        val2 = bytes_to_uint(machine.stack.pop())

        machine.stack.push(uint_to_bytes(val1 ** val2))
