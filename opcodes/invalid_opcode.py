class InvalidOpcode():
    def __init__(self, instruction):
        self.instruction = instruction.hex()
        pass
        #super().__init__(instruction)

    def total_argument_length(self):
        return 0

    def add_arguments(self, args):
        pass

    def execute(self, machine):
        import pdb; pdb.set_trace()
        return {
            'type': 'return',
            'func': 'invalid',
            'pc': machine.pc,
            'value': self.instruction
        }

    def pretty_str(self):
        return 'INVALID'
