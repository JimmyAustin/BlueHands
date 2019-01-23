from utils import int_to_bytes, bytes_to_uint, value_is_constant, uint_to_bytes
from exceptions import PathDivergenceException


def call_op(execution_context, contract, universe):
    gas = execution_context.stack.pop()
    to = execution_context.stack.pop()
    value = execution_context.stack.pop()
    in_offset = execution_context.stack.pop()
    in_size = execution_context.stack.pop()
    out_offset = execution_context.stack.pop()
    out_size = execution_context.stack.pop()

    if value_is_constant(value):
        value = bytes_to_uint(value)

    def ready_universe(universe_to_ready, to_address, from_address):
        universe_to_ready.credit_wallet_amount(to_address, value)
        universe_to_ready.debit_wallet_amount(from_address, value)

        universe_to_ready.latest_execution_context_stack().stack.push(uint_to_bytes(1))

    if value_is_constant(to):
        universe.credit_wallet_amount(to, value)
        universe.debit_wallet_amount(contract.address, value)

        execution_context.stack.push(uint_to_bytes(1))
        return
    else:
        possible_to_addresses = [x for x in universe.contracts.keys()]
        possible_universes = []
        for to_address in possible_to_addresses:
            cloned_universe = universe.clone()
            to_address_for_z3 = bytes_to_uint(to_address) if value_is_constant(to_address) else to_address
            cloned_universe.add_path_condition(to == to_address_for_z3)
            ready_universe(cloned_universe, execution_context.caller.address, to_address)
            possible_universes.append(cloned_universe)
        raise PathDivergenceException(possible_universes)


    # if len(possible_to_addresses) == 1 and len(possible_from_addresses) == 1:
    #     to_address = possible_to_addresses[0]
    #     from_address = possible_from_addresses[0]

    #     universe.credit_wallet_amount(to_address[12:], value)
    #     universe.debit_wallet_amount(contract.address, value)

    #     if value_is_constant(to_address):
    #         to_address = bytes_to_uint(to_address)
    #     if value_is_constant(from_address):
    #         from_address = bytes_to_uint(from_address)

    #     execution_context.stack.push(uint_to_bytes(1))
    #     return
    
    # cloned_universes = []

    # for from_address in possible_from_addresses:
    #     for to_address in possible_to_addresses:
    #         if from_address != to_address:
    #             cloned_universe = universe.clone()
    #             cloned_universe.add_path_condition(bytes_to_uint(from_address) == execution_context.caller)
    #             cloned_universe.add_path_condition(bytes_to_uint(to_address) == to)

    #             cloned_universe.credit_wallet_amount(to_address, value)
    #             cloned_universe.debit_wallet_amount(from_address, value)

    #             cloned_universe.latest_execution_context_stack().stack.push(uint_to_bytes(1))

    #             cloned_universes.append(cloned_universe)

    # raise PathDivergenceException(cloned_universes)

    # if value_is_constant(value):
    #     value = bytes_to_uint(value)

    # if value_is_constant(to):

    #     machine.credit_wallet_amount(to_address, value)
    #     machine.debit_wallet_amount(machine.contract_address, value)
        
    #     machine.stack.push(int_to_bytes(1))


    # new_universes = []

    # for wallet_address, wallet in universe.contracts.items():
    #     cloned = universe.clone()
    #     will_branch_universe.latest_execution_context_stack().pc = address
    #     will_branch_universe.add_path_condition(condition != 0)
    #     wont_branch_universe.add_path_condition(condition == 0)

    #     raise PathDivergenceException([will_branch_universe, wont_branch_universe])


    # if value_is_constant(value):
    #     value = bytes_to_uint(value)


    # machine.credit_wallet_amount(to_address, value)
    # machine.debit_wallet_amount(machine.contract_address, value)
    
    # machine.stack.push(int_to_bytes(1))


# class CallOpcode(Opcode):
#     def __init__(self, instruction):
#         super().__init__(instruction)

#     def execute(self, machine):
#         # This needs A LOT more work. Need to attempt to handle rentrancy for one.
#         gas = machine.stack.pop()
#         to = machine.stack.pop()
#         value = machine.stack.pop()
#         in_offset = machine.stack.pop()
#         in_size = machine.stack.pop()
#         out_offset = machine.stack.pop()
#         out_size = machine.stack.pop()
        
#         to_address = to[12:]

#         if value_is_constant(value):
#             value = bytes_to_uint(value)
#         machine.credit_wallet_amount(to_address, value)
#         machine.debit_wallet_amount(machine.contract_address, value)
        
#         machine.stack.push(int_to_bytes(1))
