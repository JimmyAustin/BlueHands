from ..opcode import Opcode


class TimestampOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        machine.stack.push(machine.invocation_symbols[-1]['timestamp'])
