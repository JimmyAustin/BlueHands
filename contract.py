from opcode_generator import next_opcode_generator
import io


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
        return [x for x in self.necessary_opcodes() if OpcodeBuilder.instruction_is_implemented(x) is False]

# def binary_to_opcodes(binary_buffer):
#     next_value = binary_buffer.read(2)
#     binary_instructions = []
#     locations = {}

#     while len(next_value) == 2:
#         print(next_value)
#         op_code = OpcodeBuilder.build(next_value)

#         argument_length = op_code.total_argument_length() * 2 # Reading in hex, but length is in bytes
#         op_code.add_arguments(binary_buffer.read(argument_length))
#         binary_instructions.append(op_code)
#         next_value = binary_buffer.read(2)
#     return binary_instructions
