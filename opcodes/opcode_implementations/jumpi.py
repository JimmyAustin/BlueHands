from ..opcode import Opcode
from utils import int_to_bytes, bytes_to_int


class JumpiOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        address = bytes_to_int(machine.stack.pop())
        condition = bytes_to_int(machine.stack.pop())

        if condition != 0:
            machine.pc = address
