from speculative_machine import SpeculativeMachine
from utils import bytes_to_int, load_binary
from universe import Universe 


def test_add_contract():
    binary_location = './contracts/build/add.bin'
    binary = load_binary(binary_location)

    universe = Universe()
    contract = universe.deploy_contract(binary)

    result = contract.execute_function('renderAdd()', [])

    result = bytes_to_int(result['value'])
    assert result == 14690
