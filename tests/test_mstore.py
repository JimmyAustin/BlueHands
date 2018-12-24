from speculative_machine import SpeculativeMachine
from utils import int_to_bytes


def test_mstore():
    program = bytes.fromhex('6009600052')
    # 0      PUSH1  => 09
    # 5      PUSH1  => 00
    # 7      MSTORE

    machine = SpeculativeMachine(program, concrete_execution=True)

    next_op = machine.get_next_opcode(step_pc=False)
    assert next_op.text == 'PUSH1'
    machine.step()
    assert machine.stack.peek() == b"\x09".rjust(32, b"\x00")

    next_op = machine.get_next_opcode(step_pc=False)
    assert next_op.text == 'PUSH1'
    machine.step()

    next_op = machine.get_next_opcode(step_pc=False)
    assert next_op.text == 'MSTORE'
    machine.step()
    assert len(machine.stack.stack) == 0
    assert len(machine.memory.data) == 32
    assert machine.memory.get(int_to_bytes(0), int_to_bytes(32)) == b"\x09".rjust(32, b"\x00")
