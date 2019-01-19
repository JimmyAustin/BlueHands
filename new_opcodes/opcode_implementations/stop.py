def stop_op(execution_context, contract, universe):
    return {
        'type': 'return',
        'func': 'stop'
    }


# class StopOpcode(Opcode):
#     def __init__(self, instruction):
#         super().__init__(instruction)

#     def execute(self, machine):
#         return {
#             'type': 'return',
#             'func': 'stop'
#         }
