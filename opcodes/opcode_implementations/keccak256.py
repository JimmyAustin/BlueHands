from ..opcode import Opcode


class Keccak256Opcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        raise NotImplementedError
        # address = machine.stack.pop()
        # value = machine.stack.pop()
        # memory = machine.memory.get(address, length)
        # from Crypto.Hash import keccak
        # keccak_hash = keccak.new(digest_bits=256)
        # keccak_hash.update('age')
        # import pdb
        # pdb.set_trace()
        # machine.stack.push()
