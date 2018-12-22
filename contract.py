from opcode_generator import next_opcode_generator
import io
from opcodes.opcode_builder import OpcodeBuilder


class Contract():
    def __init__(self, binary_buffer):
        self.opcodes = list(next_opcode_generator(binary_buffer))

    def from_binary_string(string):
        return Contract(io.StringIO(string))

    def print_opcodes(self):
        for opcode in self.opcodes:
            print(opcode.pretty_str())

    def necessary_opcodes(self):
        return set([x.text for x in self.opcodes])

    def missing_opcodes(self):
        return [x for x in self.necessary_opcodes()
                if OpcodeBuilder.instruction_is_implemented(x) is False]
