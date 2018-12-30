from ..opcode import Opcode
from utils import int_to_bytes, value_is_constant


class CallValueOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        call_value = machine.invocation_symbols[-1]['call_value']
        # if value_is_constant(call_value):
        #     import pdb; pdb.set_trace()
        #     call_value = int_to_bytes(call_value)
        machine.stack.push(call_value)


0x3fb2a74e0000000000000000000000004b0897b0513fdc7c541b6d9d7e929c4e5364d2db0000000000000000000000000000000000000000000000000000000000989680