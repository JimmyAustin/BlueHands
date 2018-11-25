from ..opcode import Opcode

class AddOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        val1 = int.from_bytes(machine.stack.pop(), 'big')
        val2 = int.from_bytes(machine.stack.pop(), 'big')
        machine.stack.push((val1+val2).to_bytes(32, 'big'))
