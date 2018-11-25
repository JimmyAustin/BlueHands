class InvalidOpcode():
    def __init__(self, instruction):
        self.instruction = instruction

    def total_argument_length(self):
        return 0

    def add_arguments(self, *args, **kwargs):
        pass

    def pretty_str(self):
        return f"INVALID {self.instruction.hex()}"
