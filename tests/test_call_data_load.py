from speculative_machine import SpeculativeMachine
from utils import bytes_to_int


def test_call_data_load():
    program = bytes.fromhex('60003560203501')
    input_string = "0000000000000000000000000000000000000000000000000000000000000005" + \
                   "0000000000000000000000000000000000000000000000000000000000000004"
    input_data = bytes.fromhex(input_string)
    # 0      PUSH1  => 00
    # 2      CALLDATALOAD
    # 3      PUSH1  => 20
    # 5      CALLDATALOAD
    # 6      ADD

    machine = SpeculativeMachine(program, input_data, concrete_execution=True)

    next_op = machine.get_next_opcode(step_pc=False)
    assert next_op.text == 'PUSH1'
    machine.step()

    next_op = machine.get_next_opcode(step_pc=False)
    assert next_op.text == 'CALLDATALOAD'
    machine.step()
    assert bytes_to_int(machine.stack.peek()) == 5

    next_op = machine.get_next_opcode(step_pc=False)
    assert next_op.text == 'PUSH1'
    machine.step()

    next_op = machine.get_next_opcode(step_pc=False)
    assert next_op.text == 'CALLDATALOAD'
    machine.step()
    assert bytes_to_int(machine.stack.peek()) == 4

    next_op = machine.get_next_opcode(step_pc=False)
    assert next_op.text == 'ADD'
    machine.step()
    assert bytes_to_int(machine.stack.peek()) == 9
