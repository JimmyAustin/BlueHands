from utils import uint_to_bytes, bytes_to_uint, value_is_constant

def add_op(execution_context, contract, universe):
    val1 = execution_context.stack.pop()
    val2 = execution_context.stack.pop()

    if value_is_constant(val1):
        val1 = bytes_to_uint(val1)
        if value_is_constant(val2):
            val2 = bytes_to_uint(val2)
            new_val = val1 + val2
            if new_val >= 2 ** 256:
                new_val -= 2 ** 256
            execution_context.stack.push(uint_to_bytes(new_val))
        else:
            execution_context.stack.push(val1 + val2)
    else:
        if value_is_constant(val2):
            val2 = bytes_to_uint(val2)
            execution_context.stack.push(val1 + val2)
        else:
            execution_context.stack.push(val1 + val2)


# class AddOpcode(Opcode):
#     def __init__(self, instruction):
#         super().__init__(instruction)

#     def execute(self, machine):
#         val1 = machine.stack.pop()
#         val2 = machine.stack.pop()

#         if value_is_constant(val1):
#             val1 = bytes_to_uint(val1)
#             if value_is_constant(val2):
#                 val2 = bytes_to_uint(val2)
#                 new_val = val1 + val2
#                 if new_val >= 2 ** 256:
#                     new_val -= 2 ** 256
#                 machine.stack.push(uint_to_bytes(new_val))
#             else:
#                 machine.stack.push(val1 + val2)
#         else:
#             if value_is_constant(val2):
#                 val2 = bytes_to_uint(val2)
#                 machine.stack.push(val1 + val2)
#             else:
#                 machine.stack.push(val1 + val2)
