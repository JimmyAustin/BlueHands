from speculative_machine import SpeculativeMachine
from utils import parse_solidity_returned_string


def test_hello_world_contract():
    binary_location = './contracts/build/helloWorld.bin'

    def load_binary(path):
        with open(path) as file_obj:
            return bytes.fromhex(file_obj.read())

    binary = load_binary(binary_location)

    machine = SpeculativeMachine(binary, concrete_execution=True)

    machine.deploy(binary)
    result = machine.execute_function_named('renderHelloWorld()', [])

    result = parse_solidity_returned_string(result.value)

    assert result == 'helloWorld'
