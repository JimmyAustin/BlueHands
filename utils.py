def int_to_bytes(val):
    return int.to_bytes(val, 32, 'big')

def bytes_to_int(val):
    return int.from_bytes(val, 'big')
