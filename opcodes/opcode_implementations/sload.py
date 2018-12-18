from ..opcode import Opcode

zero_word = bytes(32)

class SloadOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        key = machine.stack.pop()
        machine.stack.push(machine.storage.get(key))
