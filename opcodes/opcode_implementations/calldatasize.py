from ..opcode import Opcode
from utils import int_to_bytes


class CalldatasizeOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        machine.stack.push(int_to_bytes(len(machine.input)))
