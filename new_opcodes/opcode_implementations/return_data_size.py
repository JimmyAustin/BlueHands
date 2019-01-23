from utils import int_to_bytes

def return_data_size_op(execution_context, contract, universe):
    execution_context.stack.push(int_to_bytes(len(execution_context.returned_data)))
