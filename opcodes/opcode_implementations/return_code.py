from ..opcode import Opcode

class ReturnOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        address = machine.stack.pop()
        length = machine.stack.pop()
        return {
            'type': 'return',
            'func': 'return',
            'value': machine.memory.get(address, length)
        }