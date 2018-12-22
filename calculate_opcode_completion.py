from opcodes.evm_opcodes.opcodes import opcodes
from opcodes.opcode_builder import directory
from machine import Machine
implemented = 0
total = 0

for opcode_details in opcodes:
    total += 1
    text = opcode_details['text']
    bin_obj = bytes.fromhex(opcode_details['bin'])
    class_obj, extra_details = directory[text]
    opcode = class_obj(bin_obj, *extra_details)

    machine = Machine('')

    try:
        opcode.execute(machine)
    except NotImplementedError:
        print(f"Missing: {opcode_details['text']}")
    except Exception:
        implemented += 1

print(f"Implemented: {implemented}, Total: {total}")
