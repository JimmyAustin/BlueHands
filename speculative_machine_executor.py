from exceptions import PathDivergenceException, ReturnException
from z3 import Solver, SolverFor, sat, BitVecVal, Z3Exception, BitVec, simplify, Context
from speculative_machine import SpeculativeMachine, translate_to_context_if_needed
from utils import value_is_constant, pad_bytes_to_address, bytes_to_uint
from pprint import pprint
from method_identifier import identify_methods, identify_path_conditions
from multiprocessing import Queue
from multiprocessing.pool import ThreadPool
import traceback


class SpeculativeMachineExecutor():
    def __init__(self, starting_machine, should_test_for_sat_at_every_jump=False):
        starting_machine.concrete_execution = False

        self.should_test_for_sat_at_every_jump = should_test_for_sat_at_every_jump
        self.starting_machine = starting_machine
        self.branches_evaluated = 0

    def generate_single_possible_end(self, *args, **kwargs):
        return self.generate_possible_ends(*args, **kwargs).__next__

    def possible_ends(self, acceptance_criteria=[], additional_requirements=[], multithreaded=False):
        queue = Queue()
        pool = ThreadPool(8)

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
                return_value = e.value

                context = Context()
                cloned_machine = machine.clone_with_context(context)
                if multithreaded == True:
                    pool.apply_async(evaluate_machine, [queue, machine.clone(), context, e.func_type, 
                                                        return_value, additional_requirements, acceptance_criteria])
                else:
                    evaluate_machine(queue, machine, context, e.func_type, 
                                                        return_value, additional_requirements, acceptance_criteria)
                if machine.max_invocations > machine.current_invocation + 1:
                    machine.new_invocation()
                    possible_machines.append(machine)

            except Exception as e:
                raise e

        pool.close()
        pool.join()

        results = []
        while queue.empty() is False:
            results.append(queue.get())
        return results

def evaluate_machine(queue, machine, context, e_func_type, return_value, additional_requirements, acceptance_criteria):
    print("EVAL")
    try:
        if return_value is not None and value_is_constant(return_value) is True:
            return_value = BitVecVal(int.from_bytes(return_value, 'big'), 256, ctx=context)

        return_type_enum = enum_for_return_type(e_func_type)

        requirements = [*additional_requirements,
                        *acceptance_criteria]
        print('1')

        requirements.append(machine.last_return_type == return_type_enum)
        print('2')
        requirements.append(machine.attacker_wallet == get_wallet_amount(machine, machine.sender_address))
        print('3')
        requirements.append(machine.first_timestamp == machine.invocation_symbols[0]['timestamp'])
        print('4')
        requirements.append(machine.last_timestamp == machine.invocation_symbols[-1]['timestamp'])
        print('5')
                        
        if return_value is not None:
            last_return_val = translate_to_context_if_needed(machine.last_return_value, context)
            return_val = translate_to_context_if_needed(return_value, context)
            requirements.append(last_return_val == return_val)
        print('6')




        input_values = calculate_results_for_machine(
            machine, requirements=requirements, context=context)
        print("INPUT VALUES")
        print(input_values)
        if input_values:
            result = {
                #'machine': machine,
                'type': e_func_type,
                'value': str(return_value),
                'path_conditions': [x.__repr__() for x in machine.path_conditions],
                'invocations': machine.current_invocation,
                'requirements': [x.__repr__() for x in requirements],
                'methods': identify_methods(machine),
                'results': input_values
            }
            
            print(result) 
            queue.put(result)

    except Exception as exp:
        print('thread exception')
        import sys
        ex_ty, ex_ob, ex_tb = sys.exc_info()
        traceback.print_exc()
        traceback.print_tb(ex_tb)
        raise exp


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


def sated_solver_for_machine(machine, requirements=[], context=None):
    # solver = Solver()
    solver = SolverFor('QF_UFBV', ctx=context)
    all_conditions = [*machine.path_conditions, 
               *requirements,
               *getattr(machine, 'temp_path_conditions', []),
               *[v >= 0 for _, v in machine.wallet_amounts.items() if value_is_constant(v) is False]]
    for condition in all_conditions:
        if context is not None and condition.ctx != context:
            condition = condition.translate(context)
        print(condition)
        solver.add(condition)
#    solver.add(*all_conditions)
    # for condition in machine.path_conditions:
    #     pprint(condition)
    # for condition in requirements:
    #     pprint(condition)
    from datetime import datetime
    starting_time = datetime.now()
    print(f"Start Sat Check: {len(all_conditions)}")
    from pprint import pprint
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

def calculate_results_for_machine(machine, requirements=[], context=None):
    add_temp_wallet_amounts_for_variables(machine)
    solver = sated_solver_for_machine(machine, requirements, context=context)
    if solver is None:
        return None
    model = solver.model()

    grouped_inputs = [{
        'input_symbols': [],
        'model_call_data_size': None,
        'call_data_size': machine.invocation_symbols[i]['call_data_size'],
        'timestamp': None
    } for i in range(0, machine.current_invocation+1)]

    for model_input in model:
        name = model_input.name()
        if name.startswith('input_'):
            invocation = get_symbol_invocation_from_name(name)
            grouped_inputs[invocation]['input_symbols'].append(model_input)
        elif name.startswith('CallDataSize'):
            invocation = get_symbol_invocation_from_name(name)
            grouped_inputs[invocation]['model_call_data_size'] = model_input
        elif name.startswith('Timestamp'):
            invocation = get_symbol_invocation_from_name(name)
            grouped_inputs[invocation]['timestamp'] = model_input
    # if len(grouped_inputs) > 1:
    #     import pdb; pdb.set_trace()
    for grouped_input in grouped_inputs:
        inputs = sorted(grouped_input['input_symbols'], key=lambda x: x.name())
        values = [model[x] for x in inputs]
        byte_values = [int(x.as_signed_long()).to_bytes(
            32, 'big', signed=True) for x in values]
        total_value = b''.join(byte_values)

        call_data_size = grouped_input['call_data_size']

        if grouped_input['model_call_data_size'] is None:
            exists_in_model = False
        else:
            exists_in_model = True

        if call_data_size is not None and exists_in_model:
            if context is not None:
                call_data_size = call_data_size.translate(context)
            call_data_size = identify_minimum_value(solver, call_data_size)
            grouped_input['call_data_size'] = call_data_size
            total_value = total_value[:call_data_size]
        grouped_input['result'] = total_value
    return {
        'inputs': [{
            'input_data': x['result'],
            'call_data_size': x['call_data_size'],
            'timestamp': get_field(model, x['timestamp']).as_long(),
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

def identify_minimum_value(solver, field, index=None, minV=0, maxV=9000000):
    if index is None:
        index = minV + ((maxV-minV) // 2)
    
    while True:
        solver.push()
        solver.add(field < index)
        if solver.check() == sat:
            maxV = index
        else:
            minV = index
        index = minV + ((maxV-minV) // 2)
        if minV + 1 == maxV:
            return minV
        
        solver.pop()

    return None

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
