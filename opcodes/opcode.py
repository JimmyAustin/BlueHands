from .evm_opcodes.opcodes import relevant_opcode_details


class Opcode:
    def __init__(self, instruction):
        self.instruction = instruction
        details = relevant_opcode_details(instruction)
        self.text = details['text']
        self.description = details['description']
        self.arg_info = details['len_arg']
        self.args = []

    def total_argument_length(self):
        return sum(self.arg_info)

    def add_arguments(self, argument_buffer):
        if len(argument_buffer) == 0:
            return
        self.args = []
        index = 0
        for arg_length in self.arg_info:
            self.args.append(argument_buffer[index:index+arg_length])
            index += arg_length

    def pretty_str(self):
        def turn_to_hex(byte):
            return [x.hex() for x in byte]
        args = ','.join(['0x' + x.hex() for x in self.args])
        return f"{self.text} {args}"

    def execute(self, machine):
        raise NotImplementedError

    def symbolic_execute(self, machine):
        raise NotImplementedError
