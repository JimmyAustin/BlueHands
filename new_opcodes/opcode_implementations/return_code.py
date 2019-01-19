def return_op(execution_context, contract, universe):
    address = execution_context.stack.pop()
    length = execution_context.stack.pop()
    return {
        'type': 'return',
        'func': 'return',
        'value': contract.memory.get(address, length)
    }

# class ReturnOpcode(Opcode):
#     def __init__(self, instruction):
#         super().__init__(instruction)

#     def execute(self, machine):
#         address = machine.stack.pop()
#         length = machine.stack.pop()
#         return {
#             'type': 'return',
#             'func': 'return',
#             'value': machine.memory.get(address, length)
#         }
