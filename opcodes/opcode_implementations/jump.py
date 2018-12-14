from ..opcode import Opcode
from utils import int_to_bytes, bytes_to_int


class JumpOpcode(Opcode):
    def __init__(self, instruction=b'V'):
        super().__init__(instruction)

    def execute(self, machine):
        machine.pc = bytes_to_int(machine.stack.pop())
