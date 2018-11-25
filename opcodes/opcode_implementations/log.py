from ..opcode import Opcode

class LogOpcode(Opcode):
    def __init__(self, instruction, length):
        self.length = length
        super().__init__(instruction)

    def execute(self, machine):
        raise NotImplementedError