from ..opcode import Opcode


class GasOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        # TODO: Gas in general needs an overhaul and implementation
        machine.stack.push(machine.invocation_symbols[-1]['current_gas'])
