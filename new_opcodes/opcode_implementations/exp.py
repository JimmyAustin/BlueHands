from utils import uint_to_bytes, bytes_to_uint

def exp_op(execution_context, contract, universe):
    val1 = bytes_to_uint(execution_context.stack.pop())
    val2 = bytes_to_uint(execution_context.stack.pop())

    execution_context.stack.push(uint_to_bytes(val1 ** val2))


# class ExpOpcode(Opcode):
#     def __init__(self, instruction):
#         super().__init__(instruction)

#     def execute(self, machine):
#         val1 = bytes_to_uint(machine.stack.pop())
#         val2 = bytes_to_uint(machine.stack.pop())

#         machine.stack.push(uint_to_bytes(val1 ** val2))
