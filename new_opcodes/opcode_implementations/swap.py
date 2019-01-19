from ..opcode import Opcode


class SwapOpcode(Opcode):
    def __init__(self, instruction, length):
        self.length = length
        super().__init__(instruction)

    def execute(self, machine):
        top_value = machine.stack.stack[-1]
        try:
            machine.stack.stack[-1] = machine.stack.stack[-(self.length + 1)]
        except IndexError as e:
            import pdb
            pdb.set_trace()
            raise e
        machine.stack.stack[-(self.length + 1)] = top_value
