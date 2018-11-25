from ..opcode import Opcode

class MstoreOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        address = machine.stack.pop()
        value = machine.stack.pop()
        machine.memory.set(address, value)
