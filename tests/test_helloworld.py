from speculative_machine import SpeculativeMachine
from utils import parse_solidity_returned_string, load_binary
from universe import Universe 


def test_hello_world_contract():
    binary_location = './contracts/build/helloWorld.bin'
    binary = load_binary(binary_location)

    universe = Universe()
    contract = universe.deploy_contract(binary)

    result = contract.execute_function('renderHelloWorld()', [])

    result = parse_solidity_returned_string(result['value'])
    assert result == 'helloWorld'
