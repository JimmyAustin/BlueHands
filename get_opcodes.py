from contract_executor import ContractExecutor
from machine import Machine


binary_location = './contracts/build/helloWorld.bin'

def load_binary(path):
    with open(path) as file_obj:
        return bytes.fromhex(file_obj.read())

binary = load_binary(binary_location)

executor = Machine(binary)
executor.dump_opcodes()
