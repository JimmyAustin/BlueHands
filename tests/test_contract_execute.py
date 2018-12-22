from machine import Machine
from utils import bytes_to_int, int_to_bytes


def test_functionless_contract_execute():
    program = bytes.fromhex('600580600b6000396000f36005600401')
    # 0      PUSH1  => 05 # LOADER START
    # 2      DUP1
    # 3      PUSH1  => 0b
    # 5      PUSH1  => 00
    # 7      CODECOPY
    # 8      PUSH1  => 00
    # 10     RETURN       # END
    # 11     PUSH1  => 05 # THIS IS THE ACTUAL PROGRAM
    # 13     PUSH1  => 04
    # 15     ADD')

    machine = Machine(logging=True)
    machine.deploy(program)

    assert machine.program == bytes.fromhex('6005600401')

    machine.execute()

    assert bytes_to_int(machine.stack.pop()) == 9


def test_function_contract_execute():
    # Takes two int256 arguments, adds them togethor, then saves to 0x0 in storage.
    program_bytes = '606060405260e060020a6000350463a5f3c2' + \
                    '3b8114601a575b005b60243560043501600055601856'
    program = bytes.fromhex(program_bytes)
    # 0      PUSH1  => 60
    # 2      PUSH1  => 40
    # 4      MSTORE
    # 5      PUSH1  => e0
    # 7      PUSH1  => 02
    # 9      EXP
    # 10     PUSH1  => 00
    # 12     CALLDATALOAD
    # 13     DIV
    # 14     PUSH4  => a5f3c23b # THIS IS THE FUNCTION SIGNATURE
    # 19     DUP2
    # 20     EQ
    # 21     PUSH1  => 1a
    # 23     JUMPI
    # 24     JUMPDEST
    # 25     STOP
    # 26     JUMPDEST
    # 27     PUSH1  => 24
    # 29     CALLDATALOAD
    # 30     PUSH1  => 04
    # 32     CALLDATALOAD
    # 33     ADD
    # 34     PUSH1  => 00
    # 36     SSTORE
    # 37     PUSH1  => 18
    # 39     JUMP

    machine = Machine(program, logging=True)
    result = machine.execute_function_named('add(int256,int256)', [int_to_bytes(5),
                                                                   int_to_bytes(9)])
    assert result.func_type == 'stop'
    storage_result = machine.storage.get(bytes.fromhex('00'*32))
    assert bytes_to_int(storage_result) == 14
