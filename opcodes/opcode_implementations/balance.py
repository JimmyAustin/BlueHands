from ..opcode import Opcode

class BalanceOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        raise NotImplementedError