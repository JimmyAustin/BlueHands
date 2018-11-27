from stack import Stack
from memory import Memory
from storage import Storage
import io
from opcodes.opcode_builder import OpcodeBuilder
import sha3
from utils import bytes_to_int


class ReturnException(BaseException):
    def __init__(self, value, func_type):
        self.value = value
        self.func_type = func_type

class ExectionEndedException(BaseException):
    pass

class StopException(BaseException):
    pass


class Machine:
    def __init__(self, program=bytes(), input_data=bytes(), logging=True):
        self.pc = 0
        self.program = program
        self.stack = Stack()
        self.memory = Memory()
        self.storage = Storage()
        self.input = input_data
        self.logging = logging
        self.step_count = 0

    def execute_function_named(self, function_name, args):
        k = sha3.keccak_256()
        k.update(function_name.encode('utf8'))
        function_sig = bytes.fromhex(k.hexdigest()[0:8])
        return self.execute_function(function_sig, args)

    def execute_function(self, function_sig, args):
        self.pc = 0
        print(f"Executing functionsig: {function_sig.hex()}")
        self.input = bytearray(function_sig)
        for arg in args:
            self.input.extend(arg.rjust(32, b"\x00"))
        try:
            self.execute(pdb_step=False)
            return None
        except ReturnException as return_e:
            return return_e

    def deploy(self, program):
        self.program = program
        self.pc = 0
        try:
            self.execute()
        except ReturnException as return_e:
            self.program = bytes(return_e.value)
            self.pc = 0
            print("Application deployed successfully")
        except ExectionEndedException:
            print("No value was returned")
            raise ExectionEndedException

    def get_next_opcode(self, step_pc=True):
        if self.pc >= len(self.program):
            return None
        if step_pc is False:
            original_pc = self.pc

        next_value = self.read_program_bytes()
        op_code = OpcodeBuilder.build(next_value)

        argument_length = op_code.total_argument_length() # Reading in hex, but length is in bytes

        op_code.add_arguments(self.read_program_bytes(argument_length))

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
            raise ExectionEndedException('Out of code to run')
        return self.execute_opcode(next_opcode)
        

    def execute(self, pdb_step=False):
        next_opcode = self.get_next_opcode()
        while next_opcode is not None:
            if pdb_step:
                import pdb; pdb.set_trace()
            self.execute_opcode(next_opcode)
            next_opcode = self.get_next_opcode()

    def execute_opcode(self, opcode):
        self.step_count += 1
        if self.logging:
            print(f"EXECUTING: {opcode.pretty_str()}")
        result = opcode.execute(self)
        if self.logging:
            self.print_state()
        if result is None:
            return
        elif result['type'] == 'return':
            raise ReturnException(result.get('value'), result['func'])

        import pdb; pdb.set_trace()


    def print_state(self):
        print("---STACK---")
        for i, value in enumerate(reversed(self.stack.stack)):
            print(f"{i}: 0x{value.hex()}")

        print("---STORAGE---")
        for k,v in self.storage.storage.items():
            print(f"    {k.hex()}: {v.hex()}")

        print("---MEMORY---")
        for i in range(0, len(self.memory.data), 16):
            print(f"{str(i).zfill(4)} - {self.memory.data[i:i+16].hex()}")
#        print(self.memory.data)


    def dump_opcodes(self):
        next_opcode = self.get_next_opcode()
        while next_opcode is not None:
            print(next_opcode.pretty_str())
            next_opcode = self.get_next_opcode()
