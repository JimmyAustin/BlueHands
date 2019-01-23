from .opcode_implementations import *

hex_to_int = lambda hex_v: bytes.fromhex(hex_v)[0]

instruction_mapping = {
    hex_to_int('00'): ('STOP', stop_op),
    hex_to_int('01'): ('ADD', add_op),
    hex_to_int('02'): ('MUL', mul_op),
    hex_to_int('03'): ('SUB', sub_op),
    hex_to_int('04'): ('DIV', div_op),
    hex_to_int('0a'): ('EXP', exp_op),
    hex_to_int('10'): ('LT', lt_op),
    hex_to_int('11'): ('GT', gt_op),
    hex_to_int('14'): ('EQ', eq_op),
    hex_to_int('15'): ('ISZERO', iszero_op),
    hex_to_int('16'): ('AND', and_op),
    hex_to_int('17'): ('OR', or_op),
    hex_to_int('19'): ('NOT', not_op),
    hex_to_int('20'): ('KECCAK256', keccak256_op),
    hex_to_int('33'): ('CALLER', caller_op),
    hex_to_int('34'): ('CALLVALUE', callvalue_op),
    hex_to_int('35'): ('CALLDATALOAD', calldataload_op),
    hex_to_int('36'): ('CALLDATASIZE', calldatasize_op),
    hex_to_int('39'): ('CODECOPY', codecopy_op),
    hex_to_int('3D'): ('RETURNDATASIZE', return_data_size_op),
    hex_to_int('42'): ('TIMESTAMP', timestamp_op),
    hex_to_int('50'): ('POP', pop_op),
    hex_to_int('51'): ('MLOAD', mload_op),
    hex_to_int('52'): ('MSTORE', mstore_op),
    hex_to_int('54'): ('SLOAD', sload_op),
    hex_to_int('55'): ('SSTORE', sstore_op),
    hex_to_int('56'): ('JUMP', jump_op),
    hex_to_int('57'): ('JUMPI', jumpi_op),
    hex_to_int('5A'): ('GAS', gas_op),
    hex_to_int('5B'): ('JUMPDEST', jumpdest_op),
    hex_to_int('F1'): ('CALL', call_op),
    hex_to_int('F3'): ('RETURN', return_op),
    hex_to_int('FD'): ('REVERT', revert_op)
}

for i in range(32):
    instruction_mapping[96 + i] = (f"PUSH{i+1}", get_push_op_func(i+1))

for i in range(15):
    instruction_mapping[128 + i] = (f"DUP{i+1}", get_dup_op_func(i+1))

for i in range(16):
    instruction_mapping[144 + i] = (f"SWAP{i+1}", get_swap_op_func(i+1))


def get_instruction(opcode, logging=True):
    if opcode not in instruction_mapping:
        print("OPCODE NOT IMPLEMENTED WHAT THE FUCK")
        print(bytes([opcode]).hex())
        import pdb; pdb.set_trace()
    name, instruction = instruction_mapping[opcode]
    if logging:
        print(f"Executing: {name}")
    return instruction


# Contract: 3045bc24bdbe644799db5070b9eb4fd892ade69f
# attacker_wallet: 22253822587e84d4e7f2c20604dcfb3c429c3c73
# cfo_wallet: 7a346f1d953d480ae8192943a6e01719c9ff890b
