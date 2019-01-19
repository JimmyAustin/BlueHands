def not_op(execution_context, contract, universe):
    bytearr = bytearray(execution_context.stack.pop())
    for i, val in enumerate(bytearr):
        bytearr[i] = ~val % 256
    execution_context.stack.push(bytes(bytearr))
