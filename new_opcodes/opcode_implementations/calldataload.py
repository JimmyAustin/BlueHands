from utils import bytes_to_int, value_is_constant

def calldataload_op(execution_context, contract, universe):
    address = execution_context.stack.pop()
    execution_context.stack.push(execution_context.input_for_address(address))

#     if machine.concrete_execution:
#         address = bytes_to_int(machine.stack.pop())
#         call_data = machine.get_input_at_address(address)
#         machine.stack.push(call_data.ljust(32, b"\x00"))
#     else:
#         address = machine.stack.pop()
#         if value_is_constant(address) is False:
#             error = 'Dynamic address calldataload is not supported'
#             raise NotImplementedError(error)
#         machine.stack.push(machine.get_input_at_address(bytes_to_int(address)))


# class CalldataloadOpcode(Opcode):
#     def __init__(self, instruction):
#         super().__init__(instruction)

#     def execute(self, machine):
#         if machine.concrete_execution:
#             address = bytes_to_int(machine.stack.pop())
#             call_data = machine.get_input_at_address(address)
#             machine.stack.push(call_data.ljust(32, b"\x00"))
#         else:
#             address = machine.stack.pop()
#             if value_is_constant(address) is False:
#                 error = 'Dynamic address calldataload is not supported'
#                 raise NotImplementedError(error)
#             machine.stack.push(machine.get_input_at_address(bytes_to_int(address)))
