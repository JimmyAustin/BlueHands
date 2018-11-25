from ..opcode import Opcode

class RevertOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        address = int.from_bytes(machine.stack.pop(), 'big')
        length = int.from_bytes(machine.stack.pop(), 'big')
        return {
            'type': 'return',
            'value': machine.memory.get(address, length)
        }