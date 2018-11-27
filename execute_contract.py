from machine import Machine, ReturnException
from utils import bytes_to_int

binary_location = './contracts/build/add.bin'

def load_binary(path):
    with open(path) as file_obj:
        return bytes.fromhex(file_obj.read())

binary = load_binary(binary_location)

machine = Machine(binary, logging=True)
machine.deploy(binary)
result = machine.execute_function_named('renderAdd()', [])
result = bytes_to_int(result)

print(result)
