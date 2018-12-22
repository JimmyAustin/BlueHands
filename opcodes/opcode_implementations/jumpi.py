from ..opcode import Opcode
from utils import bytes_to_int, value_is_constant
from exceptions import PathDivergenceException


class JumpiOpcode(Opcode):
    def __init__(self, *args, **kwargs):
        super().__init__(b'W')

    def execute(self, machine):
        address = machine.stack.pop()
        if value_is_constant(address) is False:
            raise NotImplementedError(
                'Non concrete address is not yet implemented')
        else:
            address = bytes_to_int(address)

        condition = machine.stack.pop()
        if value_is_constant(condition) is True:
            condition = bytes_to_int(condition)

        if value_is_constant(condition):
            if condition != 0:
                machine.pc = address
            if machine.logging:
                print("Jumping" if condition != 0 else "Skipping jumping")
        else:
            if machine.concrete_execution is True:
                return
            will_branch_machine = machine
            wont_branch_machine = machine.clone()
            will_branch_machine.pc = address
            will_branch_machine.path_conditions.append(condition != 0)
            wont_branch_machine.path_conditions.append(condition == 0)

            raise PathDivergenceException(
                [will_branch_machine, wont_branch_machine])
