from exceptions import PathDivergenceException, ReturnException
from z3 import Solver, sat, BitVecVal
from speculative_machine import SpeculativeMachine
from utils import value_is_constant

class SpeculativeMachineExecutor():
    def __init__(self, starting_machine):
        starting_machine.concrete_execution = False
        starting_machine.concrete_execution = False

        self.starting_machine = starting_machine
        self.branches_evaluated = 0
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
                solvers = []
                for i, machine in enumerate(machines):
                    if sated_solver_for_machine(machine, requirements=additional_requirements):
                        print("Adding new invocation")
                        possible_machines.append(machine)
            except ReturnException as e:
                return_value = e.value
                    
                if value_is_constant(return_value) is True:
                    return_value = BitVecVal(int.from_bytes(return_value, 'big'), 256)
                else:
                    import pdb; pdb.set_trace()
                print(return_value)
                return_type_enum = enum_for_return_type(e.func_type)
                print("Doing machine again")

                requirements = [*additional_requirements,
                                *acceptance_criteria,
                                machine.last_return_type==return_type_enum,
                                machine.last_return_value==return_value]
                result = {
                        'machine': machine,
                        'type': e.func_type,
                        'value': e.value,
                        'path_conditions': machine.path_conditions,
                        'invocations': machine.current_invocation
                    }
                print(result)
                input_values = calculate_inputs_for_machine(machine, requirements=requirements)
                if input_values:
                    result['inputs'] = input_values                   
                    yield result
                else:
                    if e.func_type != "revert":
                        if machine.max_invocations > machine.current_invocation:
                            print('Adding machine back in fresh')
                            machine.new_invocation()
                            possible_machines.append(machine)

            except Exception as e:
                import pdb; pdb.set_trace()
                raise e

def sated_solver_for_machine(machine, requirements=[]):
    solver = Solver()
    solver.add(*machine.path_conditions, *requirements)
    if solver.check() != sat:
        return None
    return solver

def calculate_inputs_for_machine(machine, requirements=[]):
    solver = sated_solver_for_machine(machine, requirements)
    if solver is None:
        return None
    model = solver.model()

    grouped_inputs = [{
        'input_symbols': [],
        'call_data_size': None
    }]    
    import pdb; pdb.set_trace()
    for model_input in model:
        name = model_input.name()
        if name.startswith('input_'):
            invocation = get_symbol_invocation_from_name(name)
            grouped_inputs[invocation]['input_symbols'].append(model_input)
        elif name.startswith('CallDataSize'):
            invocation = get_symbol_invocation_from_name(name)
            grouped_inputs[invocation]['call_data_size'] = model_input

    for grouped_input in grouped_inputs:
        inputs = sorted(grouped_input['input_symbols'], key=lambda x: x.name())
        values = [model[x] for x in inputs]
        byte_values = [int(x.as_long()).to_bytes(32, 'big') for x in values]
        total_value = b''.join(byte_values)

        call_data_size = grouped_input['call_data_size']

        if call_data_size is not None:
            call_data_length = int(model[call_data_size].as_long())
            total_value = total_value[:call_data_length]
        grouped_input['result'] = total_value
    return [x['result'] for x in grouped_inputs]


def enum_for_return_type(return_type):
    if return_type == 'return':
        return SpeculativeMachine.RETURN_TYPE_RETURN
    if return_type == 'revert':
        return SpeculativeMachine.RETURN_TYPE_REVERT
    if return_type == 'stop':
        return SpeculativeMachine.RETURN_TYPE_STOP
    raise Exception

def get_symbol_invocation_from_name(name):
    # symbol names are structured like this: {symbolName}_{invocation}_{wordcount}
    components = name.split('_')
    return int(components[1])