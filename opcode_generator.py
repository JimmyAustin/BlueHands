from opcodes.opcode_builder import OpcodeBuilder


def next_opcode_generator(binary_buffer):
    next_value = binary_buffer.read(2)
    while len(next_value) == 2:
        op_code = OpcodeBuilder.build(next_value)

        # Reading in hex, but length is in bytes
        argument_length = op_code.total_argument_length() * 2
        op_code.add_arguments(bytes.fromhex(
            binary_buffer.read(argument_length)))
        yield op_code
        next_value = binary_buffer.read(2)
    raise StopIteration()
