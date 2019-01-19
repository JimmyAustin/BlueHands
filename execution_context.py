from stack import Stack
from new_opcodes import get_instruction
from utils import uint_to_bytes, bytes_to_uint, translate_ctx
from copy import deepcopy
from z3 import BitVec, Extract
from enums import EXECUTION_TYPE_CONCRETE
from exceptions import ReturnException


class ExecutionContext:

    def __init__(self, excId, contract, universe, call_method, execution_type, call_value=None,
                 input_data=None):

        self.excId = excId
        self.contract = contract
        self.universe = universe
        self.call_method = call_method
        self.execution_type = execution_type
        self.stack = Stack()
        self.pc = 0

        self.input_data = input_data
        self.call_value = call_value

        if self.execution_type == EXECUTION_TYPE_CONCRETE:
            self.__init_concrete_defaults()
        else:
            self.__init_symbolic_defaults()

    def __init_concrete_defaults(self):
        self.call_value = self.call_value or bytes(32)
        self.call_data_size = uint_to_bytes(len(self.input_data))
        if self.execution_type == EXECUTION_TYPE_CONCRETE:
            if self.input_data is None:
                raise ValueError('Must provide data (even bytes()) if execution type is concrete')

    def __init_symbolic_defaults(self):
        self.call_value = BitVec(f"{self.excId}_CallValue", 256)
        self.timestamp = BitVec(f"{self.excId}_Timestamp", 256)
        self.call_data_size = BitVec(f"{self.excId}_CallDataSize", 256)
        self.input_words = []
        self.input_words_by_index = {}

    def execute(self):
        if self.execution_type == EXECUTION_TYPE_CONCRETE:
            return self.concrete_execute()
        else:
            return self.symbolic_execute()

    def concrete_execute(self):
        while True:
            instruction_func = get_instruction(self.get_next_program_bytes(1)[0])
            return_value = instruction_func(self, self.contract, self.universe)
            if self.universe.logging:
                self.universe.dump_state()
            if return_value is not None:
                if return_value['type'] == 'return':
                    return return_value
                print(return_value)
                import pdb; pdb.set_trace()
                pass

    def symbolic_execute(self):
        while True:
            instruction_func = get_instruction(self.get_next_program_bytes(1)[0])
            return_value = instruction_func(self, self.contract, self.universe)
            self.universe.dump_state()
            if return_value is not None:
                raise ReturnException(return_value.get('value'), return_value['func'])
                # if return_value['type'] == 'return':
                #     return return_value
                # print(return_value)
                # import pdb; pdb.set_trace()
                # pass

    def get_next_program_bytes(self, count=1):
        result = self.contract.program[self.pc:self.pc+count]
        self.pc += count
        return result

    def input_for_address(self, address):
        address = bytes_to_uint(address)

        if self.execution_type == EXECUTION_TYPE_CONCRETE:
            data = self.input_data[address:address+32]
            return data.ljust(32, b"\x00")
        else:
            while (address + 32) > (len(self.input_words) * 32):
                input_address_name = len(self.input_words) * 32
                new_input = BitVec(f"{self.excId}_input_{input_address_name}", 256)

                self.input_words_by_index[len(self.input_words) * 32] = new_input
                self.input_words.append(new_input)

            if address in self.input_words_by_index:
                return self.input_words_by_index[address]

            new_input = BitVec(f"{self.excId}_input@{address}", 256)

            self.input_words_by_index[address] = new_input
            bitvec_offset = (address % 32)
            previous_bitvec = self.input_words[(address - bitvec_offset) // 32]
            next_bitvec = self.input_words[(address + (32 + bitvec_offset)) // 32]
            overlap = bitvec_offset * 8
            end = 255

            # These are indexed in the opposite of the way you would expect.
            # Example:
            # previous bitvec: a6c14f8d00000000000000000000000000000000000000000000000000000000
            # Next bitvec:     0000000f00000000000000000000000000000000000000000000000000000000
            # Desired Bitvec:  000000000000000000000000000000000000000000000000000000000000000f
            # Overlap: 4 Bytes
            # It indexes from the right side, rather then the left.
            print(f"Prev: {previous_bitvec}")
            print(f"Next: {next_bitvec}")

            self.universe.path_conditions.append(Extract(end-overlap, 0, previous_bitvec) ==
                                                 Extract(end, overlap, new_input))

            self.universe.path_conditions.append(Extract(overlap-1, 0, new_input) ==
                                                 Extract(end, end - overlap+1, next_bitvec))

            return new_input

    def clone_with_context(self, context):
        clone = deepcopy(self)

        clone.timestamp = translate_ctx(clone.timestamp, context)
        clone.call_data_size = translate_ctx(clone.call_data_size, context)

        return clone