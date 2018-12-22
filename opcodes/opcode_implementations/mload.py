from ..opcode import Opcode

bytes_32 = (32).to_bytes(32, 'big')


class MloadOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        address = machine.stack.pop()
        machine.stack.push(machine.memory.get(address, bytes_32))
