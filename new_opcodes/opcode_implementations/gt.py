from utils import uint_to_bytes, bytes_to_uint, value_is_constant, is_bitvec
from z3 import If, UGT


def gt_op(execution_context, contract, universe):
    val1 = execution_context.stack.pop()
    val2 = execution_context.stack.pop()
    if value_is_constant(val1):
        val1 = bytes_to_uint(val1)
        if value_is_constant(val2):
            val2 = bytes_to_uint(val2)
            value = 1 if val1 > val2 else 0
            execution_context.stack.push(uint_to_bytes(value))
            return
        else:
            try:
                execution_context.stack.push(If(appropriate_divide_method(val1, val2), 1, 0))
            except Exception as e:
                import pdb; pdb.set_trace()
                pass
    else:
        if value_is_constant(val2):
            val2 = bytes_to_uint(val2)
        try:
            execution_context.stack.push(If(appropriate_divide_method(val1, val2), 1, 0))
        except Exception as e:
            import pdb; pdb.set_trace()
            pass


# class GtOpcode(Opcode):
#     def __init__(self, instruction):
#         super().__init__(instruction)

#     def execute(self, machine):
#         val1 = machine.stack.pop()
#         val2 = machine.stack.pop()

#         if value_is_constant(val1):
#             val1 = bytes_to_uint(val1)
#             if value_is_constant(val2):
#                 val2 = bytes_to_uint(val2)
#                 value = 1 if val1 > val2 else 0
#                 machine.stack.push(uint_to_bytes(value))
#                 return
#             else:
#                 machine.stack.push(If(appropriate_divide_method(val1, val2), 1, 0))
#         else:
#             if value_is_constant(val2):
#                 val2 = bytes_to_uint(val2)
#             machine.stack.push(If(appropriate_divide_method(val1, val2), 1, 0))
#             #machine.stack.push(If(appropriate_divide_method(val1, val2), 1, 0))
            
#         # val1 = bytes_to_int(machine.stack.pop())
#         # val2 = bytes_to_int(machine.stack.pop())
#         # value = 1 if val1 < val2 else 0
#         # machine.stack.push(int_to_bytes(value))
def appropriate_divide_method(val1, val2):
    if is_bitvec(val1) or is_bitvec(val2):
        import pdb; pdb.set_trace()
        return UGT(val1, val2)
    else:
        try:
            return UGT(val1, val2)
            return val1 > val2
        except Exception as e:
            import pdb; pdb.set_trace()
            pass