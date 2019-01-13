from ..opcode import Opcode
from utils import uint_to_bytes, bytes_to_uint, value_is_constant, is_bitvec
from z3 import If, ULT


class LtOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        val1 = machine.stack.pop()
        val2 = machine.stack.pop()
        if value_is_constant(val1):
            val1 = bytes_to_uint(val1)
            if value_is_constant(val2):
                val2 = bytes_to_uint(val2)
                value = 1 if val1 < val2 else 0
                machine.stack.push(uint_to_bytes(value))
                return
            else:
                try:
                    machine.stack.push(If(appropriate_divide_method(val1, val2), 1, 0))
                except Exception as e:
                    import pdb; pdb.set_trace()
                    pass
        else:
            if value_is_constant(val2):
                val2 = bytes_to_uint(val2)
            try:
                machine.stack.push(If(appropriate_divide_method(val1, val2), 1, 0))
            except Exception as e:
                import pdb; pdb.set_trace()
                pass
            #machine.stack.push(If(appropriate_divide_method(val1, val2), 1, 0))
            
        # val1 = bytes_to_int(machine.stack.pop())
        # val2 = bytes_to_int(machine.stack.pop())
        # value = 1 if val1 < val2 else 0
        # machine.stack.push(int_to_bytes(value))
def appropriate_divide_method(val1, val2):
    if is_bitvec(val1) or is_bitvec(val2):
        return ULT(val1, val2)
    else:
        return val1 < val2
