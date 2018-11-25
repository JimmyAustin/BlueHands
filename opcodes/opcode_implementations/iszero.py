from ..opcode import Opcode
from utils import bytes_to_int, int_to_bytes

class IszeroOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        value = bytes_to_int(machine.stack.pop())
        value_to_push = 1 if value == 0 else 0
        machine.stack.push(int_to_bytes(value_to_push))
