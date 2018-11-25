from .opcode import Opcode

class PushOpcode(Opcode):
    def __init__(self, instruction, length):
        self.length = 0
        super().__init__(instruction)

    def execute(self, machine):
        raise NotImplementedError