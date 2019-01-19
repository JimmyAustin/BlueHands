bytes_32 = (32).to_bytes(32, 'big')

def mload_op(execution_context, contract, universe):
    address = execution_context.stack.pop()
    execution_context.stack.push(contract.memory.get(address, bytes_32))
