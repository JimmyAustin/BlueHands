from ..opcode import Opcode
from utils import int_to_bytes


class CalldatasizeOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        if machine.concrete_execution:
            length = len(machine.input)
            machine.stack.push(int_to_bytes(length))
        else:
            machine.stack.push(machine.call_data_size)
