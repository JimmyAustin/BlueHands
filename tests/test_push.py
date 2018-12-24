from speculative_machine import SpeculativeMachine
from utils import bytes_to_int


def test_push2():
    program = bytes.fromhex('61010161010201')
    # 0      PUSH2  => 0101
    # 3      PUSH2  => 0102
    # 6      ADD

    machine = SpeculativeMachine(program, concrete_execution=True)

    next_op = machine.get_next_opcode(step_pc=False)
    assert next_op.text == 'PUSH2'
    machine.step()
    assert bytes_to_int(machine.stack.peek()) == 257

    next_op = machine.get_next_opcode(step_pc=False)
    assert next_op.text == 'PUSH2'
    machine.step()
    assert bytes_to_int(machine.stack.peek()) == 258

    next_op = machine.get_next_opcode(step_pc=False)
    assert next_op.text == 'ADD'
    machine.step()
    assert bytes_to_int(machine.stack.peek()) == 515
