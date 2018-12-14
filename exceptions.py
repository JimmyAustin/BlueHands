class ReturnException(BaseException):
    def __init__(self, value, func_type):
        self.value = value
        self.func_type = func_type

class PathDivergenceException(BaseException):
    def __init__(self, possible_machines):
        self.possible_machines = possible_machines


class ExecutionEndedException(BaseException):
    pass

class StopException(BaseException):
    pass
