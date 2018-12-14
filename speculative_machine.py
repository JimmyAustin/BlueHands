from machine import Machine
from exceptions import ExecutionEndedException

class SpeculativeMachine(Machine):
    def __init__(self, inputs=[], *args, **kwargs):
        self.inputs = inputs
        super().__init__(*args, **kwargs)
        self.concrete_execution = False
        self.path_conditions = []

    # In the speculative machine, if we step and get nothing back we assume that
    # the existing machine has been modified, and no other possible machine
    # states exist. If we get a result, we pass it back. It'll be an array of
    # possible future states.
    def step(self):
        next_opcode = self.get_next_opcode()
        if next_opcode is None:
            raise ExectionEndedException('Out of code to run')
        result = self.execute_opcode(next_opcode)
        if result is None:
            return [self]
        return result

    def machine_is_reachable(self):
        import pdb; pdb.set_trace()

    def input_size(self): #Used for CallDataSizeOp
        return len(self.inputs) * 4