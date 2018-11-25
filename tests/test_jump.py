from machine import Machine
from opcode_generator import next_opcode_generator
import io
from utils import bytes_to_int

def test_jumpi():
    program = bytes.fromhex('6000356000525b600160005103600052600051600657')
    input_data = bytes.fromhex("0000000000000000000000000000000000000000000000000000000000000005")
    # 0      PUSH1  => 00
    # 2      CALLDATALOAD
    # 3      PUSH1  => 00
    # 5      MSTORE
    # 6      JUMPDEST
    # 7      PUSH1  => 01
    # 9      PUSH1  => 00
    # 11     MLOAD
    # 12     SUB
    # 13     PUSH1  => 00
    # 15     MSTORE
    # 16     PUSH1  => 00
    # 18     MLOAD
    # 19     PUSH1  => 06
    # 21     JUMPI

    machine = Machine(program, input_data)
    machine.dump_opcodes()
    machine = Machine(program, input_data)
    machine.execute()
    print(f"Step Count: {machine.step_count}")

def test_optimized_jumpi():
    program = bytes.fromhex('6000355b6001900380600357')
    input_data = bytes.fromhex("0000000000000000000000000000000000000000000000000000000000000005")
    # 0      PUSH1  => 00
    # 2      CALLDATALOAD
    # 3      JUMPDEST
    # 4      PUSH1  => 01
    # 6      SWAP1
    # 7      SUB
    # 8      DUP1
    # 9      PUSH1  => 03
    # 11     JUMPI

    machine = Machine(program, input_data)
    #machine.dump_opcodes()
    machine.execute()
    print(f"Step Count: {machine.step_count}")
