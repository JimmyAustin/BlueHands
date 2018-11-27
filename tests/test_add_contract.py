from machine import Machine
from opcode_generator import next_opcode_generator
import io
from utils import bytes_to_int

def test_add_contract():
    binary_location = './contracts/build/add.bin'

    def load_binary(path):
        with open(path) as file_obj:
            return bytes.fromhex(file_obj.read())

    binary = load_binary(binary_location)

    machine = Machine(binary, logging=True)

    machine.deploy(binary)
    result = machine.execute_function_named('renderAdd()', [])

    result = bytes_to_int(result)
    assert result == 14690
