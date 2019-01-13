from ..opcode import Opcode
from utils import value_is_constant, bytes_to_uint, uint_to_bytes


class SubOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        # val1 = int.from_bytes(machine.stack.pop(), 'big')
        # val2 = int.from_bytes(machine.stack.pop(), 'big')
        # machine.stack.push((val1-val2).to_bytes(32, 'big'))
        val1 = machine.stack.pop()
        val2 = machine.stack.pop()

        if value_is_constant(val1):
            val1 = bytes_to_uint(val1)
            if value_is_constant(val2):
                val2 = bytes_to_uint(val2)
                result = val1 - val2
                if result < 0:
                    result += 2 ** 256
                machine.stack.push(uint_to_bytes(result))
            else:
                machine.stack.push(val1 - val2)
        else:
            if value_is_constant(val2):
                val2 = bytes_to_uint(val2)
                machine.stack.push(val1 - val2)
            else:
                machine.stack.push(val1 - val2)
        print(f"ADDING: {val1} + {val2} == {machine.stack.stack[-1]}")