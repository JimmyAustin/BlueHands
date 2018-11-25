from machine import Machine, ReturnException


binary_location = './contracts/build/add.bin'

def load_binary(path):
    with open(path) as file_obj:
        return bytes.fromhex(file_obj.read())

binary = load_binary(binary_location)

executor = Machine(binary, logging=True)
try:
    executor.execute()
except:
    print("DONE")
print(executor.step_count)
import pdb; pdb.set_trace()
executor.logging=True
try:
    executor.execute_function_named('renderAdd()', [])
except ReturnException as e:
    import pdb; pdb.set_trace()
    print(f"ReturnValue - {e}, {e.value.hex()}")
except Exception as e:
    print(f"DONE - {e}")

import pdb; pdb.set_trace()