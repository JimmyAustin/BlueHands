from ..opcode import Opcode
from utils import int_to_bytes, value_is_constant

class CallValueOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        call_value = machine.call_value
        if value_is_constant(call_value):
            call_value = int_to_bytes(call_value)
        machine.stack.push(call_value)