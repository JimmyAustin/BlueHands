def int_to_bytes(val):
    return int.to_bytes(val, 32, 'big')

def bytes_to_int(val):
    return int.from_bytes(val, 'big')

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