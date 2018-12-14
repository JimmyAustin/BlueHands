from ..opcode import Opcode
from utils import int_to_bytes


class CalldatasizeOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        if machine.concrete_execution:
            length = len(machine.input)
        else:
            if len(machine.inputs) == 0:
                length = 0
            elif len(machine.inputs) == 1:
                length = 4
            else:
                length = (len(machine.inputs) - 1) * 16
                length = 1000
        machine.stack.push(int_to_bytes(length))