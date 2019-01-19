from utils import pad_bytes_to_arg, hex_or_string
from contract import Contract
from execution_context import ExecutionContext
from copy import deepcopy
from z3 import BitVec
from utils import translate_ctx
from enums import EXECUTION_TYPE_CONCRETE, EXECUTION_TYPE_SYMBOLIC, CALL_METHOD_ROOT


class Universe():
    def __init__(self, logging=True):
        self.contracts = {}
        self.execution_context_stacks = []
        self.path_conditions = []
        self.logging = logging

        self.first_timestamp = BitVec('FirstTimestamp', 256)
        self.last_timestamp = BitVec('LastTimestamp', 256)
        self.last_return_value = BitVec('LastReturnValue', 256)
        self.last_return_type = BitVec('LastReturnType', 256)


    def deploy_contract(self, binary, args=[], address=None, is_runtime=False):
        for arg in args:
            binary = binary + pad_bytes_to_arg(arg)
        
        contract = Contract(binary, address=address, universe=self)
        self.contracts[contract.address] = contract
        exec_context = ExecutionContext('deploy', contract, universe=self, 
                                        call_method=CALL_METHOD_ROOT,
                                        execution_type=EXECUTION_TYPE_CONCRETE,
                                        call_value=bytes(32),
                                        input_data=bytes())

        result = exec_context.execute()
        
        if result['type'] != 'return':
            raise Exception('Deploy Failed')

        contract.program = result['value']

        return contract

    def add_speculative_context_stack(self, target_contract_address):
        self.execution_context_stacks.append([
            ExecutionContext(f"{len(self.execution_context_stacks)}_0",
                             self.contracts[target_contract_address], 
                             universe=self, 
                             call_method=CALL_METHOD_ROOT,
                             execution_type=EXECUTION_TYPE_SYMBOLIC)
            ])

    def clone(self):
        return deepcopy(self)

    def clone_with_context(self, context):
        clone = self.clone()

        clone.path_conditions = [translate_ctx(x, context) for x in clone.path_conditions]
        clone.execution_context_stacks = [[y.clone_with_context(context) for y in x] 
                                          for x in clone.execution_context_stacks]
        clone.contracts = {k: contract.clone_with_context(context) 
                           for k, contract in clone.contracts.items()}

        clone.first_timestamp = translate_ctx(clone.first_timestamp, context)
        clone.last_timestamp = translate_ctx(clone.last_timestamp, context)
        clone.last_return_value = translate_ctx(clone.last_return_value, context)
        clone.last_return_type = translate_ctx(clone.last_return_type, context)

        return clone

    def first_execution_context_stack(self):
        return self.execution_context_stacks[0][0]

    def last_execution_context_stack(self):
        return self.execution_context_stacks[-1][0]

    def latest_execution_context_stack(self):
        return self.execution_context_stacks[-1][-1]

    def dump_state(self):
        for i, execution_context_stack in enumerate(self.execution_context_stacks):
            print("EXECUTION_CONTEXT_STACK {i}")
            for y, execution_context in enumerate(execution_context_stack):
                print("   EXECUTION_CONTEXT {i} - {execution_context.contract.address.hex()}")
                print("---STACK---")
                for i, value in enumerate(reversed(execution_context.stack.stack)):
                    print(f"{i}: 0x{hex_or_string(value)}")
        for _, contract in self.contracts.items():
            contract.dump_state()