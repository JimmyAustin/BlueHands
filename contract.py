from utils import random_address, func_sig, translate_ctx, hex_or_string
from execution_context import ExecutionContext
from z3 import BitVec
from memory import Memory
import sha3
from copy import deepcopy



class Contract():
    def __init__(self, program=None, address=None, should_deploy=None, universe=None, starting_wallet_amount=None):
        self.address = address or random_address()
        self.program = program
        
        self.memory = Memory()
        self.storage = {}

        self.universe = universe

        self.starting_wallet_amount = BitVec(f"0x{self.address.hex()}_Wallet", 256)
        self.wallet_amount = self.starting_wallet_amount

        if starting_wallet_amount is not None:
            self.wallet_amount += starting_wallet_amount

    def execute_function(self, func_name, args, call_value=bytes(32)):
        input_data = func_sig(func_name)
        for arg in args:
            input_data += args

        exec_context = ExecutionContext(self, universe=self.universe, 
                                        call_method=ExecutionContext.CALL_METHOD_ROOT,
                                        execution_type=ExecutionContext.EXECUTION_TYPE_CONCRETE,
                                        input_data=input_data)

        return exec_context.execute()

    def clone_with_context(self, context):
        clone = deepcopy(self)
        clone.starting_wallet_amount = translate_ctx(clone.starting_wallet_amount, context)
        clone.wallet_amount = translate_ctx(clone.wallet_amount, context)

        return clone

    def dump_state(self):
        print(f"CONTRACT: {self.address} - {self.wallet_amount}")
        print("---STORAGE---")
        for k, v in self.storage.items():
            print(f"    {hex_or_string(k)}: {hex_or_string(v)}")

        print("---MEMORY---")
        for i in range(0, len(self.memory.data), 16):
            print(f"{str(i).zfill(4)} - {self.memory.debug_get(i, 32)}")
