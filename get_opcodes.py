from speculative_machine import SpeculativeMachine

binary_location = './contracts/build/bankCFOVuln.bin'


def load_binary(path):
    with open(path) as file_obj:
        return bytes.fromhex(file_obj.read())


binary = load_binary(binary_location)

executor = SpeculativeMachine(binary)
executor.dump_opcodes()
