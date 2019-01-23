def sstore_op(execution_context, contract, universe):
    key = execution_context.stack.pop()
    value = execution_context.stack.pop()
    contract.storage[key] = value

# class SstoreOpcode(Opcode):
#     def __init__(self, instruction):
#         super().__init__(instruction)

#     def execute(self, machine):
#         key = machine.stack.pop()
#         value = machine.stack.pop()
#         machine.storage[key] = value
