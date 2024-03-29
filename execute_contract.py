from machine import Machine
from utils import int_to_bytes, parse_return_value
import argparse
import json


parser = argparse.ArgumentParser(description='Execute a .bin file.')
parser.add_argument('--file', '-f', required=True,  # dest='binary_location',
                    help='Path to a binary file')

parser.add_argument('--no-deploy', '-nd', action='store_true',
                    help='Path to a binary file')

parser.add_argument('--logging', '-l', action='store_true',
                    help='Should log intermediate steps')

parser.add_argument('--funcargs', action='store',
                    help="""
JSON array of individual function calls. Each array is a seperate invocation. \
First element is the function signature, the rest are arguments. Examples:
    "[['renderAdd()']]"
    "[['add(int,int)', 1 2], ['get()']]"
""".strip())

args = parser.parse_args()
print(args)


def load_binary(path):
    with open(path) as file_obj:
        return bytes.fromhex(file_obj.read())


binary = load_binary(args.file)

machine = Machine(binary, logging=args.logging)

if args.no_deploy is False:
    print("Deploying")
    machine.deploy(binary)


def load_function_argument_list(func_list):
    return json.loads(func_list)


function_calls = load_function_argument_list(args.funcargs)


for function_call in function_calls:
    def transform_argument(arg):
        if isinstance(arg, int):
            return int_to_bytes(arg)
        raise ValueError('Unknown arg type: {arg}')
    args = [transform_argument(x) for x in function_call[1:]]
    print(f"Executing: {function_call[0]} - {function_calls[1:]}")
    result = machine.execute_function_named(function_call[0], args)
    print(f"Return Type: {result.func_type}")
    if result.func_type == 'return':
        parsed_result = parse_return_value(result.value)
        print(f"Returned: {result.value.hex()} - {parsed_result}")
