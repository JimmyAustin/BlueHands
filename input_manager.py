from io import StringIO

class InputManager():
    def __init__(self, input_data):
        self.input = StringIO(input_data)

    def next(self):
        return self.input.read(32)