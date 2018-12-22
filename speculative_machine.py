from machine import Machine
from exceptions import ExecutionEndedException
from z3 import Int, BitVec, BitVecVal, Extract, Solver, sat
from utils import bytes_to_int
from stack import Stack


class SpeculativeMachine(Machine):
    RETURN_TYPE_RETURN = Int(0)
    RETURN_TYPE_REVERT = Int(1)
    RETURN_TYPE_STOP = Int(2)

    def __init__(self, inputs=[], max_invocations=1, *args, **kwargs):
        self.inputs = inputs
        self.max_invocations = max_invocations
        self.current_invocation = -1  # This goes to zero when we invoke new_invocation
        super().__init__(*args, **kwargs)
        self.concrete_execution = False
        self.path_conditions = []

        self.call_data_sizes = []
        self.call_values = []
        self.return_values = []
        self.return_types = []

        self.last_return_value = BitVec('LastReturnValue', 256)
        self.last_return_type = Int('LastReturnType')

        # self.call_data_size = Int('CallDataSize')
        # self.call_value = Int('CallValue')
        # self.return_value = BitVec('ReturnValue', 256)
        # self.return_type = Int('ReturnType')
        self.generated_words = [[]]
        self.generated_words_by_index = [{}]

        self.new_invocation()

    def new_invocation(self):
        self.pc = 0
        self.current_invocation += 1
        self.stack = Stack()
        self.generated_words.append([])
        self.generated_words_by_index.append({})
        self.call_data_sizes.append(
            Int(f"CallDataSize_{self.current_invocation}"))
        self.call_values.append(Int(f"CallValue_{self.current_invocation}"))
        self.return_values.append(
            BitVec(f"ReturnValue_{self.current_invocation}", 256))
        self.return_types.append(Int(f"ReturnType_{self.current_invocation}"))

    # In the speculative machine, if we step and get nothing back we assume that
    # the existing machine has been modified, and no other possible machine
    # states exist. If we get a result, we pass it back. It'll be an array of
    # possible future states.
    def step(self):
        next_opcode = self.get_next_opcode()
        if next_opcode is None:
            raise ExecutionEndedException('Out of code to run')
        result = self.execute_opcode(next_opcode)
        if result is None:
            return [self]
        return result

    def machine_is_reachable(self):
        import pdb
        pdb.set_trace()

    # def input_size(self): #Used for CallDataSizeOp
    #     return len(self.inputs) * 4

    def generated_words_up_to(self):
        return len(self.generated_words[self.current_invocation]) * 32

    def get_input_at_address(self, address):
        while (address + 32) > self.generated_words_up_to():
            input_address_name = len(self.generated_words[self.current_invocation]) * 32
            new_input = BitVec(f"input_{self.current_invocation}_{input_address_name}", 256)
            self.generated_words_by_index[self.current_invocation][len(
                self.generated_words[self.current_invocation]) * 32] = new_input
            self.generated_words[self.current_invocation].append(new_input)

        if address in self.generated_words_by_index[self.current_invocation]:
            return self.generated_words_by_index[self.current_invocation][address]

        new_input = BitVec(f"input@{self.current_invocation}_{address}", 256)

        self.generated_words_by_index[self.current_invocation][address] = new_input
        bitvec_offset = (address % 32)
        previous_bitvec = self.generated_words[self.current_invocation][(
            address - bitvec_offset) // 32]
        next_bitvec = self.generated_words[self.current_invocation][(
            address + (32 + bitvec_offset)) // 32]
        print(f"Bitvec offset: {bitvec_offset}")
        overlap = bitvec_offset * 8  # - 1
        print(f"Overlap: {overlap}")
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

        self.path_conditions.append(Extract(end-overlap, 0, previous_bitvec) ==
                                    Extract(end, overlap, new_input))

        self.path_conditions.append(Extract(overlap-1, 0, new_input) ==
                                    Extract(end, end - overlap+1, next_bitvec))

        return new_input

    def fix_input(self, fixed_value, fixed_starting_point):
        input_at_address = self.get_input_at_address(fixed_starting_point)
        value_length = len(fixed_value) * 8
        value_bitvecval = BitVecVal(bytes_to_int(fixed_value), value_length)
        self.path_conditions.append(value_bitvecval == input_at_address)

    def solvable(self):
        solver = Solver()
        solver.add(*self.path_conditions)
        return solver.check() == sat
