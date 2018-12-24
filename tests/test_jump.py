from speculative_machine import SpeculativeMachine
from opcodes.opcode_implementations import JumpiOpcode
from exceptions import PathDivergenceException
from z3 import Int, Solver, sat


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

    machine = SpeculativeMachine(program=program, input_data=input_data, concrete_execution=True)
    machine.dump_opcodes()
    machine = SpeculativeMachine(program=program, input_data=input_data, concrete_execution=True, logging=True)
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

    machine = SpeculativeMachine(program=program, input_data=input_data, concrete_execution=True)
    machine.execute()
    print(f"Step Count: {machine.step_count}")


def test_constant_jump():

    program = bytes.fromhex('60015b600157')
    # 0      PUSH1  => 00
    # 3      JUMPDEST
    # 4      PUSH1  => 01
    # 5      JUMPI

    machine = SpeculativeMachine(program=program, concrete_execution=True, logging=True)
    machine.step()
    machine.step()
    machine.step()
    # machines = machine.step()  # PUSH
    # machines = machines[0].step()  # JUMPDEST
    # machines = machines[0].step()  # PUSH 1
    try:
        machine.step()  # JUMPI
    except Exception:
        pass
    assert machine.pc == 1
    assert machine.step_count == 4


def test_symbolic_jump():
    x = Int('X')

    machine = SpeculativeMachine()

    machine.stack.push(x)
    machine.stack.push(b'0x3E8')  # 1000

    jumpInstruction = JumpiOpcode()
    try:
        jumpInstruction.execute(machine)
    except PathDivergenceException as path_divergence:
        machines = path_divergence.possible_machines

    assert machines is not None
    assert len(machines) == 2

    for machine in machines:
        solver = Solver()
        solver.add(*machine.path_conditions)
        assert solver.check() == sat
