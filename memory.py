from utils import value_is_constant

MEMORY_CONCRETE = 0
MEMORY_APPROX = 1


class Memory:
    def __init__(self, logging=True):
        self.data = []
        self.logging = logging

    def expand(self, expand_to):
        expand_by = expand_to - len(self.data)
        if expand_by > 0:
            self.data.extend([(MEMORY_CONCRETE, 0, None)] * expand_by)

    def set(self, address, value):
        if self.logging:
            print(f"MEMORY: SET {address} TO {value}")
        address = int.from_bytes(address, 'big')
        if value_is_constant(value):
            self.expand(address+len(value))

            for i, byte in enumerate(value):
                self.data[address+i] = (MEMORY_CONCRETE, byte, None)
        else:
            self.expand(address + (value.size() // 8))

            for i in range(value.size() // 8):
                self.data[address+i] = (MEMORY_APPROX, value, i)

    def get(self, address, length):
        address = int.from_bytes(address, 'big')
        length = int.from_bytes(length, 'big')
        if self.data[address][0] == MEMORY_APPROX:
            if self.data[address][2] == 0:  # Beginning of symbolic chunk
                return self.data[address][1]
            else:
                raise NotImplementedError(
                    'GET MSTORE ACROSS SYMBOLIC WORD NOT YET IMPLEMENTED')

        return_value = bytearray(length)

        for i, byte in enumerate(self.data[address:address+length]):
            mem_type, value, symbolic_offset = byte
            if mem_type == MEMORY_APPROX:
                raise NotImplementedError(
                    'GET MSTORE ACROSS SYMBOLIC WORD NOT YET IMPLEMENTED')
            return_value[i] = value

        return return_value

    # Length and address are ints
    def debug_get(self, address, length):
        result = ''
        for i, value in enumerate(self.data[address: address + length]):
            mem_type, value, symbolic_offset = value
            if mem_type == MEMORY_CONCRETE:
                result += 'M' + (255).to_bytes(1, 'big').hex()
            else:
                result += 'S' + str(symbolic_offset)
