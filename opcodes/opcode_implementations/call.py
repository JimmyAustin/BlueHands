from ..opcode import Opcode


class CallOpcode(Opcode):
    def __init__(self, instruction):
        super().__init__(instruction)

    def execute(self, machine):
        # This needs A LOT more work. Need to attempt to handle rentrancy for one.
        gas = machine.stack.pop()
        to = machine.stack.pop()
        value = machine.stack.pop()
        in_offset = machine.stack.pop()
        in_size = machine.stack.pop()
        out_offset = machine.stack.pop()
        out_size = machine.stack.pop()
        
        to_address = to[12:]

        machine.credit_wallet_amount(to_address, value)
        machine.debit_wallet_amount(machine.contract_address, value)
        

0x3fb2a74e00000000000000000000000014723a09acff6d2a60dcdf7aa4aff308fddc160c000000000000000000000000000000000000000000000000000000000000007b
0x3fb2a74e00000000000000000000000058434630580000000000000000000000000000000000000000000000000000000000000000000000000000004563918244f40000
