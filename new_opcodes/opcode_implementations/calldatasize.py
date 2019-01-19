from utils import int_to_bytes

def calldatasize_op(execution_context, contract, universe):
    execution_context.stack.push(execution_context.call_data_size)

# class CalldatasizeOpcode(Opcode):
#     def __init__(self, instruction):
#         super().__init__(instruction)

#     def execute(self, machine):
#         if machine.concrete_execution:
#             length = len(machine.input_data)
#             machine.stack.push(int_to_bytes(length))
#         else:
#             machine.stack.push(machine.invocation_symbols[-1]['call_data_size'])
