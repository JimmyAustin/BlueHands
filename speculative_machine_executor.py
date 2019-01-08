from exceptions import PathDivergenceException, ReturnException
from z3 import Solver, sat, BitVecVal, Z3Exception, BitVec
from speculative_machine import SpeculativeMachine
from utils import value_is_constant, pad_bytes_to_address, bytes_to_uint
from pprint import pprint
from method_identifier import identify_methods, identify_path_conditions


class SpeculativeMachineExecutor():
    def __init__(self, starting_machine, should_test_for_sat_at_every_jump=False):
        starting_machine.concrete_execution = False

        self.should_test_for_sat_at_every_jump = should_test_for_sat_at_every_jump
        self.starting_machine = starting_machine
        self.branches_evaluated = 0

    def generate_single_possible_end(self, *args, **kwargs):
        return self.generate_possible_ends(*args, **kwargs).__next__

    def possible_ends(self, *args, **kwargs):
        return list(self.generate_possible_ends(*args, **kwargs))

    def generate_possible_ends(self, acceptance_criteria=[], additional_requirements=[]):
        possible_machines = [self.starting_machine.clone()]

        while len(possible_machines) > 0:
            self.branches_evaluated += 1
            machine = possible_machines.pop()
            try:
                machine.execute()
            except PathDivergenceException as e:
                machines = e.possible_machines
                if self.should_test_for_sat_at_every_jump:
                    for i, machine in enumerate(machines):
                        if sated_solver_for_machine(machine, requirements=additional_requirements):
                            print("Adding new invocation")
                            possible_machines.append(machine)
                else:
                    for i, machine in enumerate(machines):
                        print("Adding new invocation")
                        possible_machines.append(machine)

            
            except ReturnException as e:
                print(identify_methods(machine))
                print(f"{e.func_type} = {e.value}")
                if e.should_revert:
                    continue
                # else:
                #     machine.print_state()
                return_value = e.value

                if return_value is not None and value_is_constant(return_value) is True:
                    return_value = BitVecVal(
                        int.from_bytes(return_value, 'big'), 256)

                return_type_enum = enum_for_return_type(e.func_type)

                requirements = [*additional_requirements,
                                *acceptance_criteria,
                                machine.last_return_type == return_type_enum,
                                machine.attacker_wallet == get_wallet_amount(machine, machine.sender_address)
                                ]

                if return_value is not None:
                    requirements.append(machine.last_return_value == return_value)
                result = {
                    'machine': machine,
                    'type': e.func_type,
                    'value': e.value,
                    'path_conditions': machine.path_conditions,
                    'simple_path_conditions': [],#[simplify(x) for x in machine.path_conditions],
                    'invocations': machine.current_invocation,
                    'requirements': requirements,
                    'methods': identify_methods(machine),
                }
                input_values = calculate_results_for_machine(
                    machine, requirements=requirements)
                if input_values:
                    result['results'] = input_values
                    yield result
                else:
                    if machine.max_invocations > machine.current_invocation + 1:
                        machine.new_invocation()
                        possible_machines.append(machine)

            except Exception as e:
                raise e

def get_wallet_amount(machine, address):    
    value = machine.wallet_amounts.get(address, bytes(0))
    if value_is_constant(value) is False:
        return value
    try:
        return bytes_to_uint(value)
    except TypeError:
        return value

def return_type_should_revert(return_type):
    return return_type == 'revert' or return_type == 'invalid'


def sated_solver_for_machine(machine, requirements=[]):
    solver = Solver()
    all_conditions = [*machine.path_conditions, 
               *requirements,
               *getattr(machine, 'temp_path_conditions', []),
               *[v >= 0 for _, v in machine.wallet_amounts.items() if value_is_constant(v) is False]]
    solver.add(*all_conditions)
    # for condition in machine.path_conditions:
    #     pprint(condition)
    # for condition in requirements:
    #     pprint(condition)
    from datetime import datetime
    starting_time = datetime.now()
    print(f"Start Sat Check: {len(all_conditions)}")
    from pprint import pprint
    pprint(all_conditions)
    sat_result = solver.check()
    print(f"Machine Sat Checked ({sat_result}): Took {(datetime.now()-starting_time).total_seconds()}")
    if sat_result != sat:
        return None
    return solver

def add_temp_wallet_amounts_for_variables(machine):
    # This seems like a hack. We should consider removing.
    machine.temp_wallet_amounts = {}
    machine.temp_path_conditions = []
    for k, v in machine.wallet_amounts.items():
        if value_is_constant(v) is False:
            symbol = BitVec(f"{k.hex()}_Wallet", 256)
            machine.temp_path_conditions.append(symbol == v)
            machine.temp_wallet_amounts[k] = symbol

def calculate_results_for_machine(machine, requirements=[]):
    add_temp_wallet_amounts_for_variables(machine)
    solver = sated_solver_for_machine(machine, requirements)
    if solver is None:
        return None
    model = solver.model()

    grouped_inputs = [{
        'input_symbols': [],
        'call_data_size': None
    } for i in range(0, machine.current_invocation+1)]

    for model_input in model:
        name = model_input.name()
        if name.startswith('input_'):
            invocation = get_symbol_invocation_from_name(name)
            grouped_inputs[invocation]['input_symbols'].append(model_input)
        elif name.startswith('CallDataSize'):
            invocation = get_symbol_invocation_from_name(name)
            grouped_inputs[invocation]['call_data_size'] = model_input
    # if len(grouped_inputs) > 1:
    #     import pdb; pdb.set_trace()
    for grouped_input in grouped_inputs:
        inputs = sorted(grouped_input['input_symbols'], key=lambda x: x.name())
        values = [model[x] for x in inputs]
        byte_values = [int(x.as_signed_long()).to_bytes(
            32, 'big', signed=True) for x in values]
        total_value = b''.join(byte_values)

        call_data_size = grouped_input['call_data_size']

        if call_data_size is not None:
            call_data_length = int(model[call_data_size].as_long())
            total_value = total_value[:call_data_length]
        grouped_input['result'] = total_value
    return {
        'inputs': [{
            'input_data': x['result'],
            'call_data_size': get_field(model, x['call_data_size']),
        }
        for x in grouped_inputs],
        'wallets': generate_wallet_values(machine, model)
    }

def generate_wallet_values(machine, model):
    def get_value(wallet_address, wallet_value):
        if value_is_constant(wallet_value):
            return wallet_value
        return model[machine.temp_wallet_amounts[wallet_address]]
    return {k: get_value(k, value) for k, value in machine.wallet_amounts.items()}

def get_field(model, field):
    try:
        return model[field]
    except Z3Exception:
        return None

def enum_for_return_type(return_type):
    if return_type == 'return':
        return SpeculativeMachine.RETURN_TYPE_RETURN
    if return_type == 'revert':
        return SpeculativeMachine.RETURN_TYPE_REVERT
    if return_type == 'stop':
        return SpeculativeMachine.RETURN_TYPE_STOP
    if return_type == 'invalid':
        return SpeculativeMachine.RETURN_TYPE_INVALID
    raise Exception


def get_symbol_invocation_from_name(name):
    # symbol names are structured like this: {symbolName}_{invocation}_{wordcount}
    components = name.split('_')
    return int(components[1])
