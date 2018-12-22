from ..opcode import Opcode


class PopOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        # TODO: Check we don't need to pop multiple things
        machine.stack.pop()
