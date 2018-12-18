from ..opcode import Opcode
from utils import int_to_bytes, bytes_to_int, value_is_constant

class CalldataloadOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        if machine.concrete_execution:
            address = bytes_to_int(machine.stack.pop())
            call_data = machine.get_input_at_address(address)
            machine.stack.push(call_data.ljust(32, b"\x00"))
        else:
            address = machine.stack.pop()
            if value_is_constant(address) is False:
                raise NotImplementedError('Dynamic address calldataload is not supported')
            machine.stack.push(machine.get_input_at_address(bytes_to_int(address)))
            # address = bytes_to_int(address)
            # import pdb; pdb.set_trace()
            # if address == 0:
            #     call_data = machine.inputs[0]
            # elif address == 4:
            #     call_data = machine.inputs[1]
            # else:
            #     call_data = machine.inputs[((address - 4) // 32) - 1]

            # machine.stack.push(call_data)
