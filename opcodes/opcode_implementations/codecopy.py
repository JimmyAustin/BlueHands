from ..opcode import Opcode

class CodecopyOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        memory_address = machine.stack.pop()
        code_starting_address = int.from_bytes(machine.stack.pop(), 'big')
        code_length = int.from_bytes(machine.stack.pop(), 'big')
        code = machine.program[code_starting_address: code_starting_address+code_length]
        machine.memory.set(memory_address, code)
