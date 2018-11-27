from ..opcode import Opcode

class SloadOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        key = machine.stack.pop()
        machine.stack.push(machine.storage.get(key))
