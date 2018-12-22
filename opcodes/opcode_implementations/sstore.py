from ..opcode import Opcode


class SstoreOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        key = machine.stack.pop()
        value = machine.stack.pop()
        machine.storage.set(key, value)
