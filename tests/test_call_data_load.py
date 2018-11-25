from machine import Machine
from opcode_generator import next_opcode_generator
import io
from utils import bytes_to_int

def test_call_data_load():
    program = bytes.fromhex('60003560203501')
    input_data = bytes.fromhex("00000000000000000000000000000000000000000000000000000000000000050000000000000000000000000000000000000000000000000000000000000004")
    # 0      PUSH1  => 00
    # 2      CALLDATALOAD
    # 3      PUSH1  => 20
    # 5      CALLDATALOAD
    # 6      ADD

    machine = Machine(program, input_data)

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
