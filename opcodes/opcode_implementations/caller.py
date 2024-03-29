from ..opcode import Opcode


class CallerOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        machine.stack.push(machine.sender_address)
