from utils import uint_to_bytes, value_is_constant

def gas_op(execution_context, contract, universe):
    if value_is_constant(execution_context.gas):
        execution_context.stack.push(uint_to_bytes(execution_context.gas))
    else:
        execution_context.stack.push(execution_context.gas)