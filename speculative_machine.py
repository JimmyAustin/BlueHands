import sha3
from stack import Stack
from memory import Memory
from exceptions import ExecutionEndedException, ReturnException, EmptyWalletException
from z3 import BitVec, BitVecVal, Extract, Solver, sat, BVSubNoOverflow
from utils import bytes_to_int, pad_bytes_to_address, value_is_constant, bytes_to_uint, uint_to_bytes
from stack import Stack
from opcodes.opcode_builder import OpcodeBuilder
from copy import deepcopy


class SpeculativeMachine():
    # RETURN_TYPE_RETURN = Int(0)
    # RETURN_TYPE_REVERT = Int(1)
    # RETURN_TYPE_STOP = Int(2)
    RETURN_TYPE_RETURN = 0
    RETURN_TYPE_REVERT = 1
    RETURN_TYPE_STOP = 2
    RETURN_TYPE_INVALID = 3


    def __init__(self, program=bytes(), input_data=bytes(), logging=False, call_value=0,
                 inputs=[], max_invocations=1, concrete_execution=False, wallet_amounts={},
                 sender_address=pad_bytes_to_address(b'attacker'), contract_address=pad_bytes_to_address(b'contract')):
        self.pc = 0
        self.program = program
        self.stack = Stack()
        self.memory = Memory()
        self.storage = {}
        self.logging = logging
        self.step_count = 0
        self.concrete_execution = concrete_execution

        self.sender_address = sender_address
        self.contract_address = contract_address

        self.attacker_wallet_starting = BitVec('AttackerWalletStarting', 256)
        self.attacker_wallet = BitVec('AttackerWallet', 256)
        self.wallet_amounts = wallet_amounts
        self.wallet_amounts[self.sender_address] = self.attacker_wallet_starting
        # if self.sender_address not in self.wallet_amounts:
        #     self.wallet_amounts[sender_address] = 0
        self.input_data = input_data
        #self.inputs = inputs
        self.max_invocations = max_invocations
        self.current_invocation = -1  # This goes to zero when we invoke new_invocation
        self.path_conditions = []
        self.invocation_symbols = []

        self.hash_map = {} # These are hashes that have been used in the past.

        self.return_data = bytes() # This is used for the RETURNDATASIZE and RETURNDATACOPY opcodes

        self.first_timestamp = BitVec('FirstTimestamp', 256)
        self.last_timestamp = BitVec('LastTimestamp', 256)
        self.last_return_value = BitVec('LastReturnValue', 256)
        self.last_return_type = BitVec('LastReturnType', 256)

        self.overflow_checks = []

        self.new_invocation()

    def new_invocation(self):
        print("New invocation")
        self.pc = 0
        self.current_invocation += 1
        self.stack = Stack()
        new_invocation_symbols = {
            'input_words': [],
            'input_words_by_index': {},
            'current_gas': BitVec(f"Gas_{self.current_invocation}", 256),
            'timestamp': BitVec(f"Timestamp_{self.current_invocation}", 256),

            'call_data_size': BitVec(f"CallDataSize_{self.current_invocation}", 256),
            'call_value': BitVec(f"CallValue_{self.current_invocation}", 256),
            'return_value': BitVec(f"ReturnValue_{self.current_invocation}", 256),
            'return_type': BitVec(f"ReturnType_{self.current_invocation}", 256)
        }
        if len(self.invocation_symbols) > 0:
            prev_symbols = self.invocation_symbols[-1]
            timestamp_over_prev = new_invocation_symbols['timestamp'] > prev_symbols['timestamp']
            self.path_conditions.append(timestamp_over_prev)
        self.path_conditions.append(new_invocation_symbols['call_value'] >= 0)

        self.credit_wallet_amount(self.contract_address, new_invocation_symbols['call_value'])
        self.debit_wallet_amount(self.sender_address, new_invocation_symbols['call_value'])

        self.invocation_symbols.append(new_invocation_symbols)

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
        import pdb; pdb.set_trace()

    def get_input_at_address(self, address):
        if self.concrete_execution:
            return self.input_data[address:address + 32]

        current_symbols = self.invocation_symbols[self.current_invocation]

        def generated_words_up_to():
            return len(current_symbols['input_words']) * 32

        while (address + 32) > (len(current_symbols['input_words']) * 32):
            input_address_name = len(current_symbols['input_words']) * 32
            new_input = BitVec(f"input_{self.current_invocation}_{input_address_name}", 256)

            current_symbols['input_words_by_index'][len(
                current_symbols['input_words']) * 32] = new_input
            current_symbols['input_words'].append(new_input)

        if address in current_symbols['input_words_by_index']:
            return current_symbols['input_words_by_index'][address]

        new_input = BitVec(f"input@{self.current_invocation}_{address}", 256)

        current_symbols['input_words_by_index'][address] = new_input
        bitvec_offset = (address % 32)
        previous_bitvec = current_symbols['input_words'][(
            address - bitvec_offset) // 32]
        next_bitvec = current_symbols['input_words'][(
            address + (32 + bitvec_offset)) // 32]
        overlap = bitvec_offset * 8  # - 1
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

    def clone(self):
        return deepcopy(self)

    def clone_and_restart_execution(self):
        clone = self.clone()
        clone.pc = 0
        clone.path_conditions = []
        return clone

    def dump_opcodes(self):
        next_opcode = self.get_next_opcode()
        while next_opcode is not None:
            print(next_opcode.pretty_str())
            next_opcode = self.get_next_opcode()

    def print_state(self):
        print("---STACK---")
        for i, value in enumerate(reversed(self.stack.stack)):
            print(f"{i}: 0x{hex_or_string(value)}")

        print("---STORAGE---")
        for k, v in self.storage.items():
            print(f"    {hex_or_string(k)}: {hex_or_string(v)}")

        print("---MEMORY---")
        for i in range(0, len(self.memory.data), 16):
            print(f"{str(i).zfill(4)} - {self.memory.debug_get(i, 32)}")

        print("---WALLETS---")
        for address, value in self.wallet_amounts.items():
            print(f"{address} = {value}")


    def execute_opcode(self, opcode):
        self.step_count += 1
        if self.logging:
            print(f"EXECUTING: {opcode.pretty_str()} ({self.pc})")
        result = opcode.execute(self)
        if self.logging:
            self.print_state()
        if result is None:
            return
        elif result['type'] == 'return':
            raise ReturnException(result.get('value'), result['func'])
        elif result['type'] == 'stop':
            raise ReturnException(None, result['func'])

    def execute_function_named(self, function_name, args):
        k = sha3.keccak_256()
        k.update(function_name.encode('utf8'))
        function_sig = bytes.fromhex(k.hexdigest()[0:8])
        return self.execute_deterministic_function(function_sig, args)

    def reset_temp_state(self):
        self.stack = Stack()
        self.pc = 0


    def execute_deterministic_function(self, function_sig, args=[], call_value=0, timestamp=None, 
                                       **kwargs):
        self.reset_temp_state()
        with self.deterministic_context(call_value=call_value, timestamp=timestamp, **kwargs):
            self.credit_wallet_amount(self.contract_address, call_value)
            self.pc = 0
            self.input_data = bytearray(function_sig)
            for arg in args:
                self.input_data.extend(arg.rjust(32, b"\x00"))
            print(f"EXECUTING: 0x{self.input_data.hex()}")
            try:
                self.execute(pdb_step=False)
                self.reset_temp_state()
                return None
            except ReturnException as return_e:
                self.reset_temp_state()
                if return_e.should_revert:
                    raise return_e
                else:
                    return return_e

    def deploy(self, program, args=[], **kwargs):
        with self.deterministic_context(**kwargs):
            self.program = bytearray(program)
            for arg in args:
                self.program.extend(arg.rjust(32, b"\x00"))
            self.program = bytes(self.program)
            self.pc = 0
            try:
                self.execute()
            except ReturnException as return_e:
                if return_e.func_type == 'revert':
                    raise ExecutionEndedException('Deployment Reverted')
                self.program = bytes(return_e.value)
                self.pc = 0
                print("Application deployed successfully")
            except ExecutionEndedException:
                print("No value was returned")
                raise ExecutionEndedException

    def get_next_opcode(self, step_pc=True):
        if self.pc >= len(self.program):
            return None
        if step_pc is False:
            original_pc = self.pc

        next_value = self.read_program_bytes()
        op_code = OpcodeBuilder.build(next_value)

        # Reading in hex, but length is in bytes
        argument_length = op_code.total_argument_length()

        args = self.read_program_bytes(argument_length)
        op_code.add_arguments(args)

        if step_pc is False:
            self.pc = original_pc
        return op_code

    def read_program_bytes(self, length=1):
        value = self.program[self.pc: (self.pc)+length]
        self.pc += length
        return value

    def step(self):
        next_opcode = self.get_next_opcode()
        if next_opcode is None:
            raise ExecutionEndedException('Out of code to run')
        self.execute_opcode(next_opcode)

    def execute(self, pdb_step=False):
        try:
            next_opcode = self.get_next_opcode()
            while next_opcode is not None:
                self.execute_opcode(next_opcode)
                next_opcode = self.get_next_opcode()
        except ReturnException as e:
            if e.should_revert is True:
                # Add reversion logic here?
                pass
            raise e

    def deterministic_context(self, **kwargs):
        return DeterministicContext(self, **kwargs)

    def get_wallet_amount(self, address):
        if to_address in machine.wallet_amounts:
            return machine.wallet_amounts[to_address]
        else:
            return 0

    def credit_wallet_amount(self, to_address, value):
        if to_address in self.wallet_amounts:
            self.wallet_amounts[to_address] += value
        else:
            self.wallet_amounts[to_address] = value

    def debit_wallet_amount(self, address, value):
        if address in self.wallet_amounts:
            self.path_conditions.append(self.wallet_amounts[address] >= value)
            self.wallet_amounts[address] -= value
            if value_is_constant(self.wallet_amounts[address]):
                if self.wallet_amounts[address] < 0:
                    raise EmptyWalletException(address)
            else:
                self.path_conditions.append(self.wallet_amounts[address] >= 0)
        else:
            self.wallet_amounts[address] = 0
            self.path_conditions.append(value == 0)


class DeterministicContext:
    def __init__(self, machine, sender=None, call_value=bytes(32), timestamp=None):
        self.machine = machine
        self.call_value = call_value
        self.sender = sender
        self.timestamp = timestamp
    def __enter__(self):
        current_invocation = self.machine.invocation_symbols[-1]
                
        self.previous_execution_type = self.machine.concrete_execution

        self.machine.concrete_execution = True
        
        if self.sender is not None:
            self.previous_sender = self.machine.sender_address
            self.machine.sender_address = self.sender

        if self.call_value is not None:
            self.previous_call_value = current_invocation['call_value']
            current_invocation['call_value'] = self.call_value

        if self.timestamp is not None:
            self.previous_timestamp = current_invocation['timestamp']
            current_invocation['timestamp'] = self.timestamp

    def __exit__(self, *args, **kwargs):
        current_invocation = self.machine.invocation_symbols[-1]

        self.machine.concrete_execution = self.previous_execution_type 

        if self.sender is not None:
            self.machine.sender_address = self.previous_sender

        if self.call_value is not None:        
            current_invocation['call_value'] = self.previous_call_value

        if self.timestamp is not None:
            current_invocation['timestamp'] = self.previous_timestamp

def hex_or_string(value):
    try:
        return value.hex()
    except Exception:
        return str(value)