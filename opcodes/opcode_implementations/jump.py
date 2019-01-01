from ..opcode import Opcode
from utils import bytes_to_int


class JumpOpcode(Opcode):
    def __init__(self, instruction=b'V'):
        super().__init__(instruction)

    def execute(self, machine):
        address = machine.stack.pop()
        machine.pc = bytes_to_int(address)
