from speculative_machine_executor import SpeculativeMachineExecutor
from speculative_machine import SpeculativeMachine
from z3 import BitVecVal
from utils import bytes_to_int, uint_to_bytes, int_to_bytes, parse_solidity_abi_input
from machine import Machine
from speculative_machine_executor import calculate_inputs_for_machine

# contract branchTest {
#   function renderAdd (int value) public pure returns (int) {
#     if (value == 5) {
#       return 1;
#     } else {
#       return 0;
#     }
#   }
# }

branchTest = "6080604052600436106039576000357c01000000000000000000000000000000000000" + \
             "0000000000000000000090048063a6c14f8d14603e575b600080fd5b34801560495760" + \
             "0080fd5b50607360048036036020811015605e57600080fd5b81019080803590602001" + \
             "909291905050506089565b6040518082815260200191505060405180910390f35b6000" + \
             "6005821415609b576001905060a0565b600090505b91905056fea165627a7a72305820" + \
             "bfe3c81d3efc9ae914e9b066b06eb69525eb959f79f153fb851f4ef0c293d4280029"

branchTestInputRet1 = 'a6c14f8d0000000000000000000000000000000000000000000000000000000000000005'
branchTestInputRet0 = 'a6c14f8d0000000000000000000000000000000000000000000000000000000000000000'


def test_identify_return_paths():
    program = bytes.fromhex(branchTest)
    machine = SpeculativeMachine()
    machine.program = program
    possible_ends = SpeculativeMachineExecutor(machine).possible_ends()

    # This contract has two return solutions
    # - Return, 1
    # - Return, 0

    return_count = 0

    found_1_solution = False
    found_0_solution = False

    solution_1 = 'a6c14f8d0000000000000000000000000000000000000000000000000000000000000005'
    solution_2 = 'a6c14f8d0000000000000000000000000000000000000000000000000000000000000000'

    for possible_end in possible_ends:
        if possible_end['type'] == 'return':
            return_count += 1
            input_value = possible_end['inputs'][0]
            if input_value.hex() == solution_1:
                found_1_solution = True
            if input_value.hex() == solution_2:
                found_0_solution = True

    assert found_1_solution is True
    assert found_0_solution is True

    assert return_count == 2


def test_input():
    machine = SpeculativeMachine()
    machine.fix_input(uint_to_bytes(2**256-1), 8)
    input_value = calculate_inputs_for_machine(machine, [])[0].hex()
    assert input_value == '0' * 16 + 'f' * 64 + '0' * 48


def test_have_acceptance_criteria():
    program = bytes.fromhex(branchTest)
    machine = SpeculativeMachine()
    machine.program = program

    acceptance_criteria = [
        machine.last_return_type == SpeculativeMachine.RETURN_TYPE_RETURN,
        machine.last_return_value == BitVecVal(1, 256)
    ]

    executor = SpeculativeMachineExecutor(machine)
    possible_ends = executor.possible_ends(acceptance_criteria=acceptance_criteria)
    assert len(possible_ends) == 1
    assert possible_ends[0]['inputs'][0].hex() == branchTestInputRet1


symbolicReturn = "6080604052600436106039576000357c01000000000000000000000000000000000000000" + \
                 "0000000000000000090048063db89f05114603e575b600080fd5b348015604957600080fd" + \
                 "5b50607d60048036036040811015605e57600080fd5b81019080803590602001909291908" + \
                 "03590602001909291905050506093565b6040518082815260200191505060405180910390" + \
                 "f35b600081830190509291505056fea165627a7a723058200195cb8d78a441c1418710b9c" + \
                 "0bdebcdce882dcd9a1ee12f6807e2add13ba8e10029"

# pragma solidity ^0.5.1;

# contract add_branch {
#  function renderAdd (int arg1, int arg2) public pure returns (int) {
#    return arg1 + arg2;
#  }
# }


def test_symbolic_return():
    program = bytes.fromhex(symbolicReturn)
    machine = SpeculativeMachine()
    machine.program = program

    acceptance_criteria = [
        machine.last_return_type == SpeculativeMachine.RETURN_TYPE_RETURN,
        BitVecVal(5, 256) == machine.last_return_value
    ]

    executor = SpeculativeMachineExecutor(machine)
    possible_ends = executor.possible_ends(acceptance_criteria=acceptance_criteria)

    assert len(possible_ends) == 1

    solidity_input = parse_solidity_abi_input(possible_ends[0]['inputs'][0])

    assert bytes_to_int(solidity_input['args'][0]) + bytes_to_int(solidity_input['args'][1]) == 5


# Fix the first arg to 3, should set the second arg to 2
def test_symbolic_return_fix_arg():
    program = bytes.fromhex(symbolicReturn)
    machine = SpeculativeMachine()
    machine.program = program

    machine.fix_input(int_to_bytes(3), 4)

    acceptance_criteria = [
        machine.last_return_type == SpeculativeMachine.RETURN_TYPE_RETURN,
        machine.last_return_value == BitVecVal(5, 256),
    ]

    executor = SpeculativeMachineExecutor(machine)
    possible_ends = executor.possible_ends(acceptance_criteria=acceptance_criteria)

    assert len(possible_ends) == 1
    solidity_input = [parse_solidity_abi_input(val) for val in possible_ends[0]['inputs']][0]

    assert bytes_to_int(solidity_input['args'][0]) == 3
    assert bytes_to_int(solidity_input['args'][1]) == 2


# contract Addition{
#     int x;
#     function add(int a, int b){
#         x = a + b;
#     }

#     function get() returns (int){
#         return x;
#     }
# }

# add(int,int) wont run the return opcode, but it will run "stop"

addGet = "6080604052600436106043576000357c0100000000000000000000000000000000000000" + \
         "000000000000000000900480636d4ce63c146048578063a5f3c23b146070575b600080fd" + \
         "5b348015605357600080fd5b50605a60b1565b6040518082815260200191505060405180" + \
         "910390f35b348015607b57600080fd5b5060af60048036036040811015609057600080fd" + \
         "5b81019080803590602001909291908035906020019092919050505060ba565b005b6000" + \
         "8054905090565b808201600081905550505056fea165627a7a723058204d05dba1d9a9d1" + \
         "2b46514ba154b31c5567e118051f19f3a5cc3d56b30d8967550029"


def test_intended_multifunction_usage():
    program = bytes.fromhex(addGet)
    machine = Machine(program, logging=True)
    machine.execute_function_named('add(int256,int256)', [int_to_bytes(5), int_to_bytes(3)])
    result = machine.execute_function_named('get()', [])
    assert bytes_to_int(result.value) == 8


def test_multifunction_calls():
    program = bytes.fromhex(addGet)
    machine = SpeculativeMachine(max_invocations=2)
    machine.program = program

    acceptance_criteria = [
        machine.last_return_type == SpeculativeMachine.RETURN_TYPE_RETURN,
        machine.last_return_value == BitVecVal(5, 256),
    ]
    executor = SpeculativeMachineExecutor(machine)
    possible_ends = executor.possible_ends(acceptance_criteria=acceptance_criteria)

    solidity_input = [parse_solidity_abi_input(x) for x in possible_ends[0]['inputs']]

    args = solidity_input[0]['args']
    assert solidity_input[0]['func'].hex() == 'a5f3c23b'
    assert bytes_to_int(args[0]) + bytes_to_int(args[1]) == 5
    assert solidity_input[1]['func'].hex() == '6d4ce63c'
