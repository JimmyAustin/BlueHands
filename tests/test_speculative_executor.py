from speculative_machine_executor import SpeculativeMachineExecutor
from speculative_machine import SpeculativeMachine 
from z3 import BitVecVal
from utils import bytes_to_int, int_to_bytes, parse_solidity_abi_input, func_sig, \
    eth_to_wei, ready_hex, pad_bytes_to_address, uint_to_bytes, summarise_possible_end, \
    load_binary
from universe import Universe 
from speculative_machine_executor import calculate_results_for_machine
from speculative_universe_executor import SpeculativeUniverseExecutor
from enums import RETURN_TYPE_RETURN, RETURN_TYPE_STOP

# contract branchTest {
#   function renderAdd (int value) public pure returns (int) {
#     if (value == 5) {
#       return 1;
#     } else {
#       return 0;
#     }
#   }
# }


branchTestInputRet1 = 'a6c14f8d0000000000000000000000000000000000000000000000000000000000000005'
branchTestInputRet0 = 'a6c14f8d0000000000000000000000000000000000000000000000000000000000000000'

def test_identify_return_paths():
    binary = load_binary('./contracts/build/branchTest.bin')

    universe = Universe()
    contract = universe.deploy_contract(binary)

    solutions = SpeculativeUniverseExecutor(universe).get_solutions([contract.address], [])

    # This contract has two return solutions
    # - Return, 1
    # - Return, 0

    return_count = 0

    found_1_solution = False
    found_0_solution = False

    for possible_end in solutions:
        if possible_end['type'] == 'return':
            return_count += 1
            input_value = possible_end['results']['inputs'][0]['input_data']
            if input_value.hex() == 'a6c14f8d0000000000000000000000000000000000000000000000000000000000000005':
                found_1_solution = True
            if input_value.hex() == 'a6c14f8d0000000000000000000000000000000000000000000000000000000000000000':
                found_0_solution = True

    assert found_1_solution == True
    assert found_0_solution == True

    assert return_count == 2


def test_input():
    machine = SpeculativeMachine()
    machine.fix_input(uint_to_bytes(2**256-1), 8)
    input_value = calculate_results_for_machine(machine, [])['inputs'][0]['input_data'].hex()
    assert input_value == '0' * 16 + 'f' * 64 + '0' * 48


def test_have_acceptance_criteria():
    binary = load_binary('./contracts/build/branchTest.bin')

    universe = Universe()
    contract = universe.deploy_contract(binary)


    acceptance_criteria = [
        universe.last_return_type == RETURN_TYPE_RETURN,
        universe.last_return_value == BitVecVal(1, 256)
    ]

    solutions = SpeculativeUniverseExecutor(universe).get_solutions([contract.address], 
                                                                    acceptance_criteria)

    assert len(solutions) == 1
    assert solutions[0]['results']['inputs'][0]['input_data'].hex() == branchTestInputRet1

symbolicReturn = "6080604052600436106039576000357c0100000000000000000000000000000000000000000000" + \
                 "00000000000090048063db89f05114603e575b600080fd5b348015604957600080fd5b50607d60" + \
                 "048036036040811015605e57600080fd5b81019080803590602001909291908035906020019092" + \
                 "91905050506093565b6040518082815260200191505060405180910390f35b6000818301905092" + \
                 "91505056fea165627a7a723058200195cb8d78a441c1418710b9c0bdebcdce882dcd9a1ee12f68" + \
                 "07e2add13ba8e10029"

# pragma solidity ^0.5.1;

# contract add_branch {
#  function renderAdd (int arg1, int arg2) public pure returns (int) {
#    return arg1 + arg2;
#  }
# }

def test_symbolic_return():
    binary = load_binary('./contracts/build/add_branch.bin')

    universe = Universe()
    contract = universe.deploy_contract(binary)

    acceptance_criteria = [
        universe.last_return_type == RETURN_TYPE_RETURN,
        universe.last_return_value == BitVecVal(5, 256)
    ]

    solutions = SpeculativeUniverseExecutor(universe).get_solutions([contract.address], acceptance_criteria=acceptance_criteria)

    assert len(solutions) == 1
    solidity_input = parse_solidity_abi_input(solutions[0]['results']['inputs'][0]['input_data'])
    print(solidity_input)
    assert (sum([x['val'] for x in solidity_input['args']]) % 2 ** 256) == 5

# Fix the first arg to 3, should set the second arg to 2
# def test_symbolic_return_fix_arg():
#     program = bytes.fromhex(symbolicReturn)
#     machine = SpeculativeMachine()
#     machine.program = program

#     machine.fix_input(int_to_bytes(3), 4)

#     acceptance_criteria = [
#         machine.last_return_type == SpeculativeMachine.RETURN_TYPE_RETURN,
#         machine.last_return_value == BitVecVal(5, 256),
#     ]

#     possible_ends = SpeculativeMachineExecutor(machine).possible_ends(acceptance_criteria=acceptance_criteria)

#     assert len(possible_ends) == 1
#     solidity_input = parse_solidity_abi_input(possible_ends[0]['results']['inputs'][0]['input_data'])

#     assert solidity_input['args'][0]['val'] == 3
#     assert solidity_input['args'][1]['val'] == 2



# contract Addition{
#     int x;
#     function add(int a, int b){
#         x = a + b;
#     }

#     function get() returns (int){
#         return x;
#     }
# }

addGet = "6080604052600436106043576000357c0100000000000000000000000000000000000000" + \
         "000000000000000000900480636d4ce63c146048578063a5f3c23b146070575b600080fd" + \
         "5b348015605357600080fd5b50605a60b1565b6040518082815260200191505060405180" + \
         "910390f35b348015607b57600080fd5b5060af60048036036040811015609057600080fd" + \
         "5b81019080803590602001909291908035906020019092919050505060ba565b005b6000" + \
         "8054905090565b808201600081905550505056fea165627a7a723058204d05dba1d9a9d1" + \
         "2b46514ba154b31c5567e118051f19f3a5cc3d56b30d8967550029"

def test_multifunction_calls():
    binary = load_binary('./contracts/build/Addition.bin')

    universe = Universe()
    contract = universe.deploy_contract(binary)

    acceptance_criteria = [
        universe.last_return_type == RETURN_TYPE_RETURN,
        universe.last_return_value == BitVecVal(5, 256)
    ]

    solutions = SpeculativeUniverseExecutor(universe).get_solutions([contract.address], acceptance_criteria=acceptance_criteria)

    assert len(solutions) == 1
    
    solution_inputs = solutions[0]['results']['inputs']
    
    assert solution_inputs[0]['solidity_abi_input']['func_info']['name'] == 'add(int256,int256)'
    assert solution_inputs[1]['solidity_abi_input']['func_info']['name'] == 'get()'

    assert (sum([x['val'] for x in solution_inputs[0]['solidity_abi_input']['args']]) % 2 ** 256) == 5


set_add = """
6080604052348015600f57600080fd5b5060043610604f576000357c0100000000
00000000000000000000000000000000000000000000000090048063846719e014
6054578063e5c19b2d146093575b600080fd5b607d600480360360208110156068
57600080fd5b810190808035906020019092919050505060be565b604051808281
5260200191505060405180910390f35b60bc6004803603602081101560a7576000
80fd5b810190808035906020019092919050505060cc565b005b60008160005401
9050919050565b806000819055505056fea165627a7a723058205566f68bff9591
ef5f4cc9b1103d0675626cb0cfc616b15088aa7615e7557c550029
"""
# contract set_add{
#     int x;
#     function set(int a) public{
#         x = a;
#     }

#     function get(int b) public returns (int) {
#         return x + b;
#     }
# }

def test_setting_up_before():
    binary = load_binary('./contracts/build/set_add.bin')

    universe = Universe()
    contract = universe.deploy_contract(binary)

    acceptance_criteria = [
        universe.last_return_type == RETURN_TYPE_RETURN,
        universe.last_return_value == BitVecVal(5, 256)
    ]

    contract.execute_function('set(int256)', args=[int_to_bytes(2)])

    solutions = SpeculativeUniverseExecutor(universe, max_invocations=1).get_solutions([contract.address], acceptance_criteria=acceptance_criteria)

    assert len(solutions) == 1
    
    solution_inputs = solutions[0]['results']['inputs']
    
    assert solution_inputs[0]['solidity_abi_input']['func_info']['name'] == 'get(int256)'
    assert solution_inputs[0]['solidity_abi_input']['args'][0]['val'] == 3


passwordWithdraw = """
608060405234801561001057600080fd5b50610110806100206000396000f3fe60
80604052600436106039576000357c010000000000000000000000000000000000
0000000000000000000000900480637e62eab814603b575b005b34801560465760
0080fd5b50607060048036036020811015605b57600080fd5b8101908080359060
2001909291905050506072565b005b600581141560e1573373ffffffffffffffff
ffffffffffffffffffffffff1661c3506040518060000190506000604051808303
8185875af1925050503d806000811460d8576040519150601f19603f3d01168201
6040523d82523d6000602084013e60dd565b606091505b5050505b5056fea16562
7a7a7230582058c1ef81d9b28ab7d579c27b0cedcc5de2ac7129808b044fc3b054
d8de41d5fb0029"""

def test_can_get_money_out():
    binary = load_binary('./contracts/build/password_withdraw.bin')

    universe = Universe()
    contract = universe.deploy_contract(binary)

    # Deposit the money we are going to steal.
    universe.credit_wallet_amount(contract.address, 50000000)

    attacker_wallet = universe.deploy_wallet(is_attacker=True)

    acceptance_criteria = [
        attacker_wallet.wallet == 50000
    ]

    executor = SpeculativeUniverseExecutor(universe, max_invocations=1)
    solutions = executor.get_solutions([contract.address], acceptance_criteria=acceptance_criteria)
 
    assert len(solutions) == 1

    solution_inputs = solutions[0]['results']['inputs']
    assert solution_inputs[0]['solidity_abi_input']['args'][0]['val'] == 5
    assert solutions[0]['results']['wallets'][attacker_wallet.address] == 50000
    assert solutions[0]['results']['wallets'][contract.address] == 50000000 - 50000



address_params = """
6080604052348015600f57600080fd5b50600436106045576000357c010
00000000000000000000000000000000000000000000000000000009004
8063ad065eb514604a575b600080fd5b608960048036036020811015605
e57600080fd5b81019080803573ffffffffffffffffffffffffffffffff
ffffffff16906020019092919050505060a3565b6040518082151515158
15260200191505060405180910390f35b60003373ffffffffffffffffff
ffffffffffffffffffffff168273fffffffffffffffffffffffffffffff
fffffffff1614905091905056fea165627a7a723058200620c506360505
30b34094229cfc58c4f5d4f348776688a6589ae65f4c72f3830029
"""

# pragma solidity ^0.5.1;

# contract address_return {
#  function canIdentifySender (address randomAddress) public returns (bool) {
#    return randomAddress == msg.sender;
#  }
# }

def test_address_param_values():
    binary = load_binary('./contracts/build/address_return.bin')

    universe = Universe()
    contract = universe.deploy_contract(binary)

    attacker_wallet = universe.deploy_wallet(is_attacker=True)

    acceptance_criteria = [
        universe.last_return_type == SpeculativeMachine.RETURN_TYPE_RETURN,
        universe.last_return_value == BitVecVal(1, 256),
    ]

    executor = SpeculativeUniverseExecutor(universe, max_invocations=1)
    solutions = executor.get_solutions([contract.address], acceptance_criteria=acceptance_criteria)

    assert len(solutions) == 1

    solution_input = solutions[0]['results']['inputs'][0]['solidity_abi_input']

    assert solution_input['func'].hex() == 'ad065eb5'
    assert solution_input['args'][0]['val'] == attacker_wallet.address.hex()


bankCFOVuln = """
60806040526004361061005c576000357c0100000000000000000000000000000000000000000000000000000000900480632e1a7d4d146100615780633fb2a74e1461009c5780634e0a3379146100f7578063d0e30db014610148575b600080fd5b34801561006d57600080fd5b5061009a6004803603602081101561008457600080fd5b8101908080359060200190929190505050610152565b005b3480156100a857600080fd5b506100f5600480360360408110156100bf57600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff1690602001909291908035906020019092919050505061015f565b005b34801561010357600080fd5b506101466004803603602081101561011a57600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff1690602001909291905050506101c8565b005b61015061020b565b005b61015c338261025a565b50565b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff161415156101ba57600080fd5b6101c4828261025a565b5050565b806000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff16021790555050565b34600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008282540192505081905550565b80600160008473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054101515156102a857600080fd5b80600160008473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020600082825403925050819055503373ffffffffffffffffffffffffffffffffffffffff168160405180600001905060006040518083038185875af1925050503d8060008114610353576040519150601f19603f3d011682016040523d82523d6000602084013e610358565b606091505b505050505056fea165627a7a723058207f3a8cdec7be9086d2af51b930cc2155e17027e4802c324dc4bf18f40e506e010029
"""

# pragma solidity ^0.5.1;

# contract bankCFOVuln {
#     address cfo;
#     mapping (address => uint) deposits;
    
#     function setCFO(address newCFO) public {
#         cfo = newCFO;
#     }
    
#     function deposit() payable public {
#         deposits[msg.sender] += msg.value;
#     }

#     function _withdraw(address withdrawAddress, uint withdraw_amount) private {
#         require(deposits[withdrawAddress] >= withdraw_amount);
#         deposits[withdrawAddress] -= withdraw_amount;
#         msg.sender.call.value(withdraw_amount);
#     }

#     function withdraw(uint amount) public {
#         _withdraw(msg.sender, amount);
#     }

#     function cfoWithdraw(address withdraw_address, uint amount) public {
#         require(msg.sender == cfo);
#         _withdraw(withdraw_address, amount);
#     }
# }



def test_attack_actually_exists():
    binary = load_binary('./contracts/build/bankCFOVuln.bin')

    universe = Universe()
    contract = universe.deploy_contract(binary)
        
    attacker_wallet = universe.deploy_wallet(is_attacker=True)
    cfo_wallet = universe.deploy_wallet(starting_wallet_amount=eth_to_wei(5))

    result = contract.execute_function('setCFO(address)', args=[cfo_wallet.address],
                              sender=cfo_wallet.address)
    assert result['func'] == 'stop'

    result = contract.execute_function('deposit()', args=[],
                              call_value=int_to_bytes(eth_to_wei(5)), sender=cfo_wallet.address)
    assert result['func'] == 'stop'

    result = contract.execute_function('setCFO(address)', args=[attacker_wallet.address],
                              sender=attacker_wallet.address)

    assert result['func'] == 'stop'
    result = contract.execute_function('cfoWithdraw(address,uint256)', 
                              args=[cfo_wallet.address, int_to_bytes(eth_to_wei(5))],
                              sender=attacker_wallet.address)
    assert result['func'] == 'stop'

    assert universe.contracts[attacker_wallet.address].wallet_amount == eth_to_wei(5)


def test_wallet_transfers_easy_mode():
    binary = load_binary('./contracts/build/bankCFOVuln.bin')

    universe = Universe()
    contract = universe.deploy_contract(binary)
    
    attacker_wallet = universe.deploy_wallet(is_attacker=True)
    cfo_wallet = universe.deploy_wallet(starting_wallet_amount=eth_to_wei(5))

    contract.execute_function('setCFO(address)', args=[cfo_wallet.address],
                              sender=cfo_wallet.address)

    contract.execute_function('deposit()', args=[],
                              call_value=int_to_bytes(eth_to_wei(5)), sender=cfo_wallet.address)

    contract.execute_function('setCFO(address)', args=[attacker_wallet.address],
                              sender=attacker_wallet.address)

    acceptance_criteria = [
        attacker_wallet.wallet > 0
    ]

    executor = SpeculativeUniverseExecutor(universe, max_invocations=1)
    solutions = executor.get_solutions([contract.address], acceptance_criteria=acceptance_criteria)

    assert len(solutions) == 1

    solution_input = solutions[0]['results']['inputs'][0]['solidity_abi_input']

    assert solution_input['func_info']['name'] == 'cfoWithdraw(address,uint256)'
    assert solution_input['args'][0]['val'] == cfo_wallet.address.hex()
    assert solution_input['args'][1]['val'] > 0

    # program = ready_hex(bankCFOVuln)
    # machine = SpeculativeMachine(program=program, max_invocations=1, logging=False)

    # cfo = pad_bytes_to_address(b'XCF0X')
    # print("CFO:", cfo.hex())
    # machine.execute_deterministic_function(func_sig('setCFO(address)'),
    #                                        args=[cfo],
    #                                        call_value=0,
    #                                        sender=cfo)
    # machine.execute_deterministic_function(func_sig('deposit()'),
    #                                        args=[],
    #                                        call_value=(eth_to_wei(5)),
    #                                        sender=cfo)
    # machine.execute_deterministic_function(func_sig('setCFO(address)'),
    #                                        args=[machine.sender_address],
    #                                        call_value=0,
    #                                        sender=machine.sender_address)
    # acceptance_criteria = [
    #     machine.attacker_wallet > machine.attacker_wallet_starting
    # ]
    # machine.pc = 0
    # possible_ends = SpeculativeMachineExecutor(machine).possible_ends(acceptance_criteria=acceptance_criteria)
    # assert len(possible_ends) == 1
    # summary = summarise_possible_end(possible_ends[0])
    # assert summary['inputs'][0]['data']['func_info']['name'] == 'cfoWithdraw(address,uint256)'
    # assert summary['inputs'][0]['data']['args'][0]['val'] == cfo.hex()
    # assert summary['inputs'][0]['data']['args'][1]['val'] > 0

def test_wallet_transfers_hard_mode():
    binary = load_binary('./contracts/build/bankCFOVuln.bin')

    universe = Universe()
    contract = universe.deploy_contract(binary)
    
    attacker_wallet = universe.deploy_wallet(is_attacker=True)
    cfo_wallet = universe.deploy_wallet(starting_wallet_amount=eth_to_wei(5))

    contract.execute_function('setCFO(address)', args=[cfo_wallet.address],
                              sender=cfo_wallet.address)

    contract.execute_function('deposit()', args=[],
                              call_value=int_to_bytes(eth_to_wei(5)), sender=cfo_wallet.address)

    # contract.execute_function('setCFO(address)', args=[attacker_wallet.address],
    #                           sender=attacker_wallet.address)

    acceptance_criteria = [
        attacker_wallet.wallet > 0
    ]

    executor = SpeculativeUniverseExecutor(universe, max_invocations=2)
    solutions = executor.get_solutions([contract.address], acceptance_criteria=acceptance_criteria)

    import pdb; pdb.set_trace()
    assert len(solutions) == 1
    # solution_input = solutions[0]['results']['inputs'][0]['solidity_abi_input']

    # assert solution_input['func_info']['name'] == 'cfoWithdraw(address,uint256)'
    # assert solution_input['args'][0]['val'] == cfo_wallet.address.hex()
    # assert solution_input['args'][1]['val'] > 0




    program = ready_hex(bankCFOVuln)
    machine = SpeculativeMachine(program=program, max_invocations=2, logging=False)

    cfo = pad_bytes_to_address(b'XCF0X')
    print("CFO:", cfo.hex())
    machine.execute_deterministic_function(func_sig('setCFO(address)'),
                                           args=[cfo],
                                           call_value=0,
                                           sender=cfo)
    machine.execute_deterministic_function(func_sig('deposit()'),
                                           args=[],
                                           call_value=(eth_to_wei(5)),
                                           sender=cfo)

    acceptance_criteria = [
        machine.attacker_wallet > machine.attacker_wallet_starting
    ]
    machine.pc = 0
    possible_ends = SpeculativeMachineExecutor(machine).possible_ends(acceptance_criteria=acceptance_criteria)

    summary = summarise_possible_end(possible_ends[0])

    assert summary['inputs'][0]['data']['func_info']['name'] == 'setCFO(address)'
    assert summary['inputs'][0]['data']['args'][0]['val'] == machine.sender_address.hex()

    assert summary['inputs'][1]['data']['func_info']['name'] == 'cfoWithdraw(address,uint256)'
    assert summary['inputs'][1]['data']['args'][0]['val'] == cfo.hex()
    assert summary['inputs'][1]['data']['args'][1]['val'] > 0
