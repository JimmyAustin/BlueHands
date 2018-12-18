from ..opcode import Opcode

class RevertOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        address = machine.stack.pop()
        length = machine.stack.pop()
        return {
            'type': 'return',
            'func': 'revert',
            'value': machine.memory.get(address, length)
        }