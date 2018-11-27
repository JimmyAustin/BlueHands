from ..opcode import Opcode

class CalldataloadOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        address = int.from_bytes(machine.stack.pop(), 'big')
        calldata = machine.input[address: address+32]
        ncd = calldata.ljust(32, b"\x00")
        ncd2  = calldata.rjust(32, b"\x00")
        calldata = ncd
        machine.stack.push(calldata)
