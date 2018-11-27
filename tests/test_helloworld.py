from machine import Machine
from opcode_generator import next_opcode_generator
import io
from utils import bytes_to_int, parse_solidity_returned_string

def test_hello_world_contract():
    binary_location = './contracts/build/helloWorld.bin'

    def load_binary(path):
        with open(path) as file_obj:
            return bytes.fromhex(file_obj.read())

    binary = load_binary(binary_location)

    machine = Machine(binary, logging=False)

    machine.deploy(binary)
    result = machine.execute_function_named('renderHelloWorld()', [])
    result = parse_solidity_returned_string(result.value)
    assert result == 'helloWorld'
