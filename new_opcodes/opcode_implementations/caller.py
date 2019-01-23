def caller_op(execution_context, contract, universe):
    caller = execution_context.caller
    caller = getattr(caller, 'address', caller)
    execution_context.stack.push(caller)
