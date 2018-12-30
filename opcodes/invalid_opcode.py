class InvalidOpcode():
    def __init__(self, instruction):
        pass
        #super().__init__(instruction)

    def total_argument_length(self):
        return 0

    def add_arguments(self, args):
        pass

    def execute(self, machine):
        return {
            'type': 'return',
            'func': 'invalid',
            'value': bytes()
        }

    def pretty_str(self):
        return 'INVALID'
