from ..opcode import Opcode
from utils import uint_to_bytes, value_is_constant


class CallValueOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        call_value = machine.invocation_symbols[-1]['call_value']
        if value_is_constant(call_value):
            try:
                call_value = uint_to_bytes(call_value)
            except TypeError:
                pass
        machine.stack.push(call_value)

