from utils import value_is_constant, bytes_to_uint, hex_or_string
from itertools import chain
from exceptions import PathDivergenceException


zero_word = bytes(32)

def sload_op(execution_context, contract, universe):
    key = execution_context.stack.pop()

    if key in contract.storage:
        execution_context.stack.push(contract.storage[key])
        return

    if value_is_constant(key):
        execution_context.stack.push(bytes(32))
        return

    # Non constant that hasn't been found. Duplicate the world for all possible values
    new_universes = []
    print(f"--Storage pivot ({len(contract.storage)})")

    for k, v in contract.storage.items():
        print(f"{hex_or_string(k)} - {v}")
        new_universe = universe.clone()
        new_universe.contracts[contract.address].storage[k] = v
        if value_is_constant(k):
            new_universe.path_conditions.append(bytes_to_uint(k) == key)
        else:
            new_universe.path_conditions.append(k == key)

        new_universe.latest_execution_context_stack().stack.push(v)
        new_universes.append(new_universe)

    raise PathDivergenceException(new_universes)


# class SloadOpcode(Opcode):
#     def __init__(self, instruction):
#         super().__init__(instruction)

#     def execute(self, machine):
#         key = machine.stack.pop()

#         if key in machine.storage:
#             machine.stack.push(machine.storage[key])
#             return

#         if value_is_constant(key):
#             machine.stack.push(bytes(32))
#             return

#         # Non constant that hasn't been found. Duplicate the world for all possible values
#         new_machines = []
#         print(f"--Storage pivot ({len(machine.storage)})")

#         for k, v in machine.storage.items():
#             print(f"{k.hex()} - {v}")
#             new_machine = machine.clone()
#             new_machine.storage[k] = v
#             new_machine.path_conditions.append(bytes_to_uint(k) == key)
#             new_machine.stack.push(v)
#             new_machines.append(new_machine)

#         raise PathDivergenceException(new_machines)
