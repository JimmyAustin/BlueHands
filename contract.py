from utils import random_address, func_sig, translate_ctx, hex_or_string, \
    uint_to_bytes, pad_bytes_to_arg_front
from execution_context import ExecutionContext
from z3 import BitVec
from memory import Memory
import sha3
from copy import deepcopy
from enums import CALL_METHOD_ROOT, EXECUTION_TYPE_CONCRETE


class Contract():
    def __init__(self, program=None, address=None, should_deploy=None, universe=None, starting_wallet_amount=None):
        self.address = address or random_address()
        self.program = program
        
        self.memory = Memory()
        self.storage = {}

        self.universe = universe


        # Wallet_Amount is the value we adjust through execution of the contract, wallet is a 
        # z3 bitvec we can chuck into the solver (along with a equality to wallet_amount, so we can
        # predefine constraints)
        self.wallet_amount = starting_wallet_amount or 0
        self.wallet = BitVec(f"0x{self.address.hex()}_Wallet", 256)


    def execute_function(self, func_name, args, call_value=0, sender=None, timestamp=None):
        input_data = func_sig(func_name)
        for arg in args:
            input_data += pad_bytes_to_arg_front(arg)

        if sender is not None:
            self.universe.debit_wallet_amount(sender, call_value)
            self.universe.sender_address = sender

        self.universe.credit_wallet_amount(self.address, call_value)

        exec_context = ExecutionContext(excId='deterministic', contract=self, universe=self.universe, 
                                        call_method=CALL_METHOD_ROOT,
                                        execution_type=EXECUTION_TYPE_CONCRETE,
                                        input_data=input_data,
                                        call_value=call_value,
                                        caller=sender, timestamp=timestamp)

        return exec_context.execute()

    def clone_with_context(self, context):
        clone = deepcopy(self)
        #clone.starting_wallet_amount = translate_ctx(clone.starting_wallet_amount, context)
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
