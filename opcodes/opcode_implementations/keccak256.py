from ..opcode import Opcode
import sha3


class Keccak256Opcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        address = machine.stack.pop()
        length = machine.stack.pop()
        memory_value = machine.memory.get(address, length)
        k = sha3.keccak_256()
        k.update(memory_value)
        machine.stack.push(k.digest())
