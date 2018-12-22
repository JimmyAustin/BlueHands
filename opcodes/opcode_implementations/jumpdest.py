from ..opcode import Opcode


class JumpdestOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        # Instruction does nothing
        pass
        # address = machine.stack.pop()
        # import pdb; pdb.set_trace()
        # raise NotImplementedError
