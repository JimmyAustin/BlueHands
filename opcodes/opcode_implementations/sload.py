from ..opcode import Opcode
from utils import value_is_constant, bytes_to_int
from itertools import chain
from exceptions import PathDivergenceException


zero_word = bytes(32)

class SloadOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        key = machine.stack.pop()

        if key in machine.storage:
            machine.stack.push(machine.storage[key])
            return

        if value_is_constant(key):
            machine.stack.push(bytes(32))
            return

        # Non constant that hasn't been found. Duplicate the world for all possible values
        new_machines = []
        print(f"--Storage pivot ({len(machine.storage)})")

        for k, v in machine.storage.items():
            print(f"{k.hex()} - {v}")
            new_machine = machine.clone()
            new_machine.storage[k] = v
            new_machine.path_conditions.append(bytes_to_int(k) == key)
            new_machine.stack.push(v)
            new_machines.append(new_machine)

        raise PathDivergenceException(new_machines)
