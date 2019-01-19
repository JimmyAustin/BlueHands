from utils import bytes_to_int

def jump_op(execution_context, contract, universe):
    address = execution_context.stack.pop()
    execution_context.pc = bytes_to_int(address)

# class JumpOpcode(Opcode):
#     def __init__(self, instruction=b'V'):
#         super().__init__(instruction)

#     def execute(self, machine):
#         address = machine.stack.pop()
#         machine.pc = bytes_to_int(address)
