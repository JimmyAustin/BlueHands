import sha3
from string import hexdigits

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
    return {
        'func': input_value[0:4],
        'args': [input_value[x:x+32] for x in range(4, len(input_value), 32)]
    }

def func_sig(function_name):
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