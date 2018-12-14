from ..opcode import Opcode
from utils import int_to_bytes, bytes_to_int, value_is_constant

class CalldataloadOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        if machine.concrete_execution:
            address = int.from_bytes(machine.stack.pop(), 'big')
            call_data = machine.input[address: address+32]
            machine.stack.push(call_data.ljust(32, b"\x00"))

            # ncd = call_data.ljust(32, b"\x00")
            # ncd2  = call_data.rjust(32, b"\x00")
            # call_data = ncd
            # machine.stack.push(call_data)
        else:
            address = machine.stack.pop()
            if value_is_constant(address) is False:
                raise NotImplementedError('Dynamic address calldataload is not supported')
            address = bytes_to_int(address)
            import pdb; pdb.set_trace()
            if address == 0:
                call_data = machine.inputs[0]
            elif address == 4:
                call_data = machine.inputs[1]
            else:
                call_data = machine.inputs[((address - 4) // 32) - 1]

            machine.stack.push(call_data)
