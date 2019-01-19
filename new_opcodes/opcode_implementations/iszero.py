from utils import bytes_to_int, int_to_bytes, value_is_constant, bv1, bv0
from z3 import If

def iszero_op(execution_context, contract, universe):
    value = execution_context.stack.pop()
    if value_is_constant(value):
        value = bytes_to_int(value)
        value_to_push = int_to_bytes(1 if value == 0 else 0)
    else:
        value_to_push = If(value == 0, bv1, bv0)
    execution_context.stack.push(value_to_push)
