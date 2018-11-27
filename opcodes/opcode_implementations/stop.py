from ..opcode import Opcode

class StopOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        return {
            'type': 'return',
            'func': 'stop'
        }
