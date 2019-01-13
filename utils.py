import sha3
from string import hexdigits
from z3 import Int2BV, BitVecVal, BitVec


def uint_to_bytes(val):
    return int.to_bytes(val, 32, 'big', signed=False)


def int_to_bytes(val):
    return int.to_bytes(val, 32, 'big', signed=True)


def bytes_to_int(val):
    return int.from_bytes(val, 'big', signed=True)


def bytes_to_uint(val):
    return int.from_bytes(val, 'big', signed=False)


def parse_return_value(result):
    if len(result) == 0:
        return None
    if len(result) == 32:
        return bytes_to_int(result)
    return parse_solidity_returned_string(result)


def parse_solidity_returned_string(result):
    offset = bytes_to_int(result[0:32])
    length = bytes_to_int(result[32:64])
    return result[32+offset:32+offset+length].decode('ascii')


def value_is_constant(value):
    # Determines if the value passed is a constant or symbolic value
    if isinstance(value, int) or isinstance(value, bytes) or isinstance(value, bytearray):
        return True
    return False


def parse_solidity_abi_input(input_value):
    if len(input_value) == 0:
        return None
    func_sig = input_value[0:4]

    result = {        'func': func_sig,
        'args': [input_value[x:x+32] for x in range(4, len(input_value), 32)]
    }

    name = name_for_function_sig(func_sig.hex())
    if name:
        result['name'] = name
    return result


def parse_solidity_abi_input(input_value):
    if len(input_value) == 0:
        return None
    func_sig = input_value[0:4]

    result = {'func': func_sig}

    func_info = information_for_function_sig(func_sig.hex())
    result['func_info'] = func_info

    args = [input_value[x:x+32] for x in range(4, len(input_value), 32)]
    if len(func_info['arg_types']) == 0:
        func_info['arg_types'] = [None for x in args]

    result['args'] = [parse_arg(arg, arg_type) for arg, arg_type
                      in zip(args, func_info['arg_types'])]

    return result

def parse_input(input_value):
    return {
        'data': parse_solidity_abi_input(input_value['input_data']),
        'timestamp': input_value['timestamp']
    }

def parse_arg(raw_arg, arg_type):
    arg = raw_arg
    if arg_type == 'uint256':
        arg = bytes_to_uint(raw_arg)

    if arg_type == 'int256':
        arg = bytes_to_int(raw_arg)

    if arg_type == 'address':
        arg = raw_arg[12:].hex() # Address are of len 20, but arg is len 32.

    return {
        'raw': raw_arg,
        'val': arg,
        'type': arg_type or 'Unknown'
    }

def summarise_possible_end(possible_end):
    inputs = [parse_input(input_val) for input_val 
                   in possible_end['results']['inputs']]

    return {
        'inputs': inputs
    }


def func_sig(function_name):
    if function_name == 'constructor':
        return bytes()
    k = sha3.keccak_256()
    k.update(function_name.encode('utf8'))
    return bytes.fromhex(k.hexdigest()[0:8])

# Convert eth amount to wei
def eth_to_wei(eth_amount):
    return eth_amount * 1000000000000000000

def pad_bytes_to_address(value):
    return value + bytes(20 - len(value))

# Removes random white space, and gets it ready as bytes.
def ready_hex(value):
    return bytes.fromhex(''.join([x for x in value if x in hexdigits]))    

def get_hex(value):
    try:
        return value.hex()
    except Exception:
        return value

# It seems the base implementation of inv2bv creates 256 seperate variables, 
# but we can shortcut this process if the value being handed in is a if statement

def opt_int2bv(value):
    # if value.decl().name() == 'if':
    #     children = value.children()
        
    import pdb; pdb.set_trace()
    return Int2BV(value, 256)

def information_for_function_sig(sig):
    return method_table.get(sig, {
        'name': f"Unknown Method: {sig}",
        'arg_types': []
    })


bv0 = BitVecVal(0, 256)
bv1 = BitVecVal(1, 256)

def load_binary(path):
    with open(path) as file_obj:
        return bytes.fromhex(file_obj.read())

def build_method_table():
    methods = {
        '27e235e3': 'balances(address)',
        '3fb2a74e': 'cfoWithdraw(address,uint256)',
        'd0e30db0': 'deposit()',
        '4e0a3379': 'setCFO(address)',
        '3ccfd60b': 'withdraw()',
        '2e1a7d4d': 'withdraw(uint256)',
        '7e62eab8': 'withdraw(int256)',
        '6d4ce63c': 'get()',
        '846719e0': 'get(int256)',
        'e5c19b2d': 'set(int256)',
        'a5f3c23b': 'add(int256,int256)',
        'ad065eb5': 'canIdentifySender(address)',
        'db89f051': 'renderAdd(uint256,uint256)',
        '79af55e4': 'increaseLockTime(uint256)',
        'a4beda63': 'lockTime(address)'
    }

    def get_arguments(sig):
        index = sig.find('(')
        args = sig[index+1:-1]
        return args.split(',')

    return {k: {
        'name': v,
        'arg_types': get_arguments(v)
    } for k,v in methods.items()}

method_table = build_method_table()

def is_bitvec(val):
    if val.__class__ == BitVec:
        return True
    if val.__class__ == BitVecVal:
        return True
    return False