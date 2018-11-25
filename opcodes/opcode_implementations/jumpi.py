from ..opcode import Opcode

class JumpiOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        address = int.from_bytes(machine.stack.pop(), 'big')
        condition = int.from_bytes(machine.stack.pop(), 'big')
        if condition != 0:
            machine.pc = address
            print("Jumping")
        else:
            print("Skipping jump")