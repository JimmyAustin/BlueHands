from ..opcode import Opcode
from utils import int_to_bytes

class CallvalueOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        wei = 0
        machine.stack.push(int_to_bytes(wei))