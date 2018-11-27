from ..opcode import Opcode

class NotOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        #This doesnt seem like the fastest way of doing this.
        bytearr = bytearray(machine.stack.pop())
        for i, val in enumerate(bytearr):
            bytearr[i] = ~val % 256
        machine.stack.push(bytes(bytearr))
