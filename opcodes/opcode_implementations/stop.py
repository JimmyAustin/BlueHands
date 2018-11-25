from ..opcode import Opcode

class StopOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        raise ValueError()
#        raise NotImplementedError