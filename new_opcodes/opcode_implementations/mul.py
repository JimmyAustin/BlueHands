from utils import uint_to_bytes, bytes_to_uint, value_is_constant

def mul_op(execution_context, contract, universe):
    val1 = execution_context.stack.pop()
    val2 = execution_context.stack.pop()

    if value_is_constant(val1):
        val1 = bytes_to_uint(val1)
        if value_is_constant(val2):
            val2 = bytes_to_uint(val2)
            execution_context.stack.push(uint_to_bytes(val1 * val2))
        else:
            execution_context.stack.push(val1 * val2)
    else:
        if value_is_constant(val2):
            val2 = bytes_to_uint(val2)
            execution_context.stack.push(val1 * val2)
        else:
            execution_context.stack.push(val1 * val2)
