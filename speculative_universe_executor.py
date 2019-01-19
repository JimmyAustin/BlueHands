from exceptions import PathDivergenceException, ReturnException
from z3 import Solver, SolverFor, sat, BitVecVal, Z3Exception, BitVec, simplify, Context
from utils import value_is_constant, pad_bytes_to_address, bytes_to_uint, translate_ctx, uint_to_bytes
from pprint import pprint
from method_identifier import identify_methods, identify_path_conditions
from multiprocessing import Queue
from multiprocessing.pool import ThreadPool
import traceback
from execution_context import ExecutionContext
from enums import *


class SpeculativeUniverseExecutor():
    def __init__(self, universe, max_invocations=1, multithreaded=True):
        self.universe = universe
        self.multithreaded = multithreaded
        self.max_invocations = max_invocations

    def get_solutions(self, target_contract_addresses, acceptance_criteria):
        queue = Queue()
        pool = ThreadPool(8)

        possible_universes = []
        for target_contract_address in target_contract_addresses:
            universe = self.universe.clone()
            universe.add_speculative_context_stack(target_contract_address)
            possible_universes.append(universe)

        while len(possible_universes) != 0:
            next_universe = possible_universes.pop()
            try:
                next_universe.latest_execution_context_stack().execute()
            except PathDivergenceException as e:
                universes = e.possible_universes

                for i, universe in enumerate(universes):
                    print("Adding new invocation")
                    possible_universes.append(universe)
            except ReturnException as e:
                #print(identify_methods(universe))
                print(f"{e.func_type} = {e.value}")
                if e.should_revert:
                    continue
                return_value = e.value

                context = Context()
                cloned_universe = next_universe.clone_with_context(context)
                if self.multithreaded == True:
                    pool.apply_async(evaluate_universe, [queue, cloned_universe, context, e.func_type, 
                                     return_value, acceptance_criteria])
                else:
                    evaluate_universe(queue, cloned_universe, context, e.func_type, 
                                      return_value, acceptance_criteria)
                if self.max_invocations > len(universe.execution_context_stacks) + 1:
                    for target_contract_address in target_contract_addresses:
                        universe = self.universe.clone()
                        universe.add_speculative_context_stack(target_contract_address)
                        possible_universes.append(universe)

        pool.close()
        pool.join()

        results = []
        while queue.empty() is False:
            results.append(queue.get())
        return results



def evaluate_universe(queue, universe, context, e_func_type, return_value, acceptance_criteria):
    print("EVAL")
    try:
        if return_value is not None and value_is_constant(return_value) is True:
            return_value = BitVecVal(int.from_bytes(return_value, 'big'), 256, ctx=context)

        return_type_enum = enum_for_return_type(e_func_type)

        requirements = [*acceptance_criteria]
        requirements.append(translate_ctx(universe.last_return_type, context) == 
                            translate_ctx(return_type_enum, context))
        requirements.append(translate_ctx(universe.first_timestamp, context) == 
                            translate_ctx(universe.first_execution_context_stack().timestamp, context))
        requirements.append(translate_ctx(universe.last_timestamp, context) == 
                            translate_ctx(universe.last_execution_context_stack().timestamp, context))                        

        if return_value is not None:
            last_return_val = translate_ctx(universe.last_return_value, context)
            return_val = translate_ctx(return_value, context)
            requirements.append(last_return_val == return_val)
        input_values = calculate_results_for_universe(universe, requirements=requirements,
                                                      context=context)
        if input_values:
            result = {
                #'machine': machine,
                'type': e_func_type,
                'value': str(return_value),
                # 'path_conditions': [x.__repr__() for x in machine.path_conditions],
                # 'invocations': machine.current_invocation,
                # 'requirements': [x.__repr__() for x in requirements],
                'methods': identify_methods(universe),
                'results': input_values,
                #'results': str(input_values)
            }
            queue.put(result)

    except Exception as exp:
        print('thread exception')
        import sys
        ex_ty, ex_ob, ex_tb = sys.exc_info()
        traceback.print_exc()
        traceback.print_tb(ex_tb)
        raise exp


def add_temp_wallet_amounts_for_variables(universe, context):
    # This seems like a hack. We should consider removing.
    universe.temp_wallet_amounts = {}
    universe.temp_path_conditions = []
    for address, contract in universe.contracts.items():
        if value_is_constant(contract.wallet_amount) is False:
            symbol = BitVec(f"{address.hex()}_Wallet", 256, ctx=context)
            universe.temp_path_conditions.append(symbol == contract.wallet_amount)
            universe.temp_wallet_amounts[address] = symbol

def calculate_results_for_universe(universe, requirements=[], context=None):
    add_temp_wallet_amounts_for_variables(universe, context)
    solver = sated_solver_for_universe(universe, requirements, context=context)
    if solver is None:
        return None
    model = solver.model()

    indexed_model = {x.name(): model[x] for x in model}

    def build_execution_context_stack_input_summary(exec_context_stack):
        base_context = exec_context_stack[0]
        input_data = bytes()
        for word in base_context.input_words:
            input_data += uint_to_bytes(indexed_model[word.__repr__()].as_long())

        call_data_size = 0
        if base_context.call_data_size.__repr__() in indexed_model:
            call_data_size = identify_minimum_value(solver, base_context.call_data_size)
            input_data = input_data[:call_data_size]

        return {
            'input_data': input_data,
            'call_data_size': call_data_size,
            'timestamp': long_if_not_none(indexed_model[base_context.timestamp.__repr__()])
        }

    return {
        'inputs': [build_execution_context_stack_input_summary(x) 
                   for x in universe.execution_context_stacks],
        'wallets': generate_wallet_values(universe, indexed_model)
    }

    grouped_inputs = [{
        'input_symbols': [],
        'model_call_data_size': None,
        'call_data_size': universe.invocation_symbols[i]['call_data_size'],
        'timestamp': None
    } for i in range(0, universe.current_invocation+1)]

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
                call_data_size = translate_ctx(call_data_size, context)
            call_data_size = identify_minimum_value(solver, call_data_size)
            grouped_input['call_data_size'] = call_data_size
            total_value = total_value[:call_data_size]
        grouped_input['result'] = total_value
    return {
        'inputs': [{
            'input_data': x['result'],
            'call_data_size': x['call_data_size'],
            'timestamp': long_if_not_none(get_field(model, x['timestamp'])),
        }
        for x in grouped_inputs],
        'wallets': generate_wallet_values(universe, model)
    }

def generate_wallet_values(universe, model):
    def get_value(wallet_address, wallet_value):
        if value_is_constant(wallet_value):
            return wallet_value
        value = model[universe.temp_wallet_amounts[wallet_address].__repr__()]
        if getattr(value, 'as_long', None) is not None:
            return value.as_long()
        return value
    return {address: get_value(address, contract.wallet_amount) for address, contract 
            in universe.contracts.items()}


def sated_solver_for_universe(universe, requirements=[], context=None):
    #solver = Solver(ctx=context)
    solver = SolverFor('QF_UFBV', ctx=context)
    all_conditions = [*universe.path_conditions, 
               *requirements,
               *getattr(universe, 'temp_path_conditions', []),
               *[contract.wallet_amount >= 0 for _, contract 
                 in universe.contracts.items() 
                 if value_is_constant(contract.wallet_amount) is False]]
    for condition in all_conditions:
        if context is not None:
            condition = translate_ctx(condition, context)
        solver.add(condition)

#    solver.add(*all_conditions)
    # for condition in universe.path_conditions:
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


def enum_for_return_type(return_type):
    if return_type == 'return':
        return RETURN_TYPE_RETURN
    if return_type == 'revert':
        return RETURN_TYPE_REVERT
    if return_type == 'stop':
        return RETURN_TYPE_STOP
    if return_type == 'invalid':
        return RETURN_TYPE_INVALID
    raise Exception


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


def long_if_not_none(val):
    if val is None:
        return val
    return val.as_long()
