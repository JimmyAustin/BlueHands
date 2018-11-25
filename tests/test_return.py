from machine import Machine, ReturnException
from opcode_generator import next_opcode_generator
import io


def test_return():
    # Example from https://github.com/CoinCulture/evm-tools/blob/master/analysis/guide.md
    program = bytes.fromhex("60096000526001601ff3")
    # 0      PUSH1  => 09
    # 5      PUSH1  => 00
    # 7      MSTORE
    # 8      PUSH1  => 01
    # 10     PUSH1  => 1f
    # 12     RETURN'

    machine = Machine(program)
    
    for i in range(5):
        machine.step()
    next_op = machine.get_next_opcode(step_pc=False)
    
    assert next_op.text == 'RETURN'
    try:
        result = machine.step()
        assert False
    except ReturnException as return_exception:
        assert return_exception.value[0] == 0x9
