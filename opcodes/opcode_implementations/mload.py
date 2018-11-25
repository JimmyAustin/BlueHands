from ..opcode import Opcode

class MloadOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        address = int.from_bytes(machine.stack.pop(), 'big')
        machine.stack.push(machine.memory.get(address, 32))
