from ..opcode import Opcode
import sha3
from utils import value_is_constant


class Keccak256Opcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        address = machine.stack.pop()
        length = machine.stack.pop()
        memory_value = machine.memory.get(address, length)
        if value_is_constant(memory_value):
            k = sha3.keccak_256()
            k.update(memory_value)
            machine.stack.push(k.digest())
        else:
            if memory_value.size() == 256:
                machine.stack.push(memory_value)                
            else:
                raise NotImplementedError('Cant hash symbols not of bitvec size 256')
