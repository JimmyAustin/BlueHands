class Memory:
    def __init__(self):
        self.data = bytearray()


    def set(self, address, value):
        address = int.from_bytes(address, 'big')
        # while (address + 32) > len(self.data):
        #     self.data += (b"\x00" * 32)
        # for i in range(0,32):
        #     self.data[address + i] = value[i]
        self.data[address:address+len(value)] = value#.rjust(32, b"\x00")

    # def set(self, address, value):
    #     address = int.from_bytes(address, 'big')
    #     while (address + 32) > len(self.data):
    #         self.data += (b"\x00" * 32)
    #     # for i in range(0,32):
    #     #     self.data[address + i] = value[i]
    #     self.data[address:address+32] = value.rjust(32, b"\x00")

    def get(self, address, length):
        return self.data[address:address+length]