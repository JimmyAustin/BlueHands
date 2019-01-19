def mstore_op(execution_context, contract, universe):
    address = execution_context.stack.pop()
    value = execution_context.stack.pop()
    contract.memory.set(address, value)
