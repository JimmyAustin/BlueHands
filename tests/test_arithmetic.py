from machine import Machine
from opcodes.opcode_implementations import AddOpcode, SubOpcode

def test_add():
    program = bytes.fromhex('6003600401')

    machine = Machine(program)

    next_op = machine.get_next_opcode(step_pc=False)
    assert next_op.text == 'PUSH1'
    machine.step()

    next_op = machine.get_next_opcode(step_pc=False)
    assert next_op.text == 'PUSH1'
    machine.step()

    next_op = machine.get_next_opcode(step_pc=False)
    assert next_op.text == 'ADD'
    machine.step()

    value = machine.stack.pop()

    assert value == b"\x07".rjust(32, b"\x00")


def test_sub():
    program = bytes.fromhex('6003600403')

    machine = Machine(program)

    next_op = machine.get_next_opcode(step_pc=False)
    assert next_op.text == 'PUSH1'
    machine.step()

    next_op = machine.get_next_opcode(step_pc=False)
    assert next_op.text == 'PUSH1'
    machine.step()

    next_op = machine.get_next_opcode(step_pc=False)
    assert next_op.text == 'SUB'
    machine.step()
    
    value = machine.stack.pop()

    assert value == b"\x01".rjust(32, b"\x00")
