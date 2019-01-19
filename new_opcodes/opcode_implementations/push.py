from ..opcode import Opcode


class PushOpcode(Opcode):
    def __init__(self, instruction, length):
        self.length = length
        super().__init__(instruction)

    def execute(self, machine):
        machine.stack.push(self.args[0])
