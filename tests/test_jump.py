from machine import Machine
from speculative_machine import SpeculativeMachine 
from opcode_generator import next_opcode_generator
import io
from utils import bytes_to_int
from z3 import *
from opcodes.opcode_implementations import JumpiOpcode
from exceptions import PathDivergenceException, ReturnException

def test_jumpi():
    program = bytes.fromhex('6000356000525b600160005103600052600051600657')
    input_data = bytes.fromhex("0000000000000000000000000000000000000000000000000000000000000005")
    # 0      PUSH1  => 00
    # 2      CALLDATALOAD
    # 3      PUSH1  => 00
    # 5      MSTORE
    # 6      JUMPDEST
    # 7      PUSH1  => 01
    # 9      PUSH1  => 00
    # 11     MLOAD
    # 12     SUB
    # 13     PUSH1  => 00
    # 15     MSTORE
    # 16     PUSH1  => 00
    # 18     MLOAD
    # 19     PUSH1  => 06
    # 21     JUMPI

    machine = Machine(program, input_data)
    machine.dump_opcodes()
    machine = Machine(program, input_data)
    machine.execute()
    print(f"Step Count: {machine.step_count}")

def test_optimized_jumpi():
    program = bytes.fromhex('6000355b6001900380600357')
    input_data = bytes.fromhex("0000000000000000000000000000000000000000000000000000000000000005")
    # 0      PUSH1  => 00
    # 2      CALLDATALOAD
    # 3      JUMPDEST
    # 4      PUSH1  => 01
    # 6      SWAP1
    # 7      SUB
    # 8      DUP1
    # 9      PUSH1  => 03
    # 11     JUMPI

    machine = Machine(program, input_data)
    #machine.dump_opcodes()
    machine.execute()
    print(f"Step Count: {machine.step_count}")


def test_constant_jump__only():

    program = bytes.fromhex('60015b600157')
    # 0      PUSH1  => 00
    # 3      JUMPDEST
    # 4      PUSH1  => 01
    # 5      JUMPI

    machine = SpeculativeMachine(program=program, logging=True)
    #machine.dump_opcodes() 
    machines = machine.step() # PUSH
    machines = machines[0].step() # JUMPDEST
    machines = machines[0].step() # PUSH 1
    try:
        machines = machines[0].step() # JUMPI
    except Exception:
        pass
    assert machine.pc == 1
    assert machine.step_count == 4

def test_symbolic_jump__only():
    x = Int('X')

    machine = SpeculativeMachine()

    machine.stack.push(x)
    machine.stack.push(b'0x3E8') # 1000
    
    jumpInstruction = JumpiOpcode()
    didFail = False
    try:
        jumpInstruction.execute(machine)
    except PathDivergenceException as path_divergence:
        didFail = True
        machines = path_divergence.possible_machines

    assert machines is not None
    assert len(machines) == 2

    for machine in machines:
        solver = Solver()
        solver.add(*machine.path_conditions)
        assert solver.check() == sat

def test_identify_path_that_returns_1__only():
    program = "6080604052600436106039576000357c01000000000000000000000000000000000000" + \
              "0000000000000000000090048063a6c14f8d14603e575b600080fd5b34801560495760" + \
              "0080fd5b50607360048036036020811015605e57600080fd5b81019080803590602001" + \
              "909291905050506089565b6040518082815260200191505060405180910390f35b6000" + \
              "6005821415609b576001905060a0565b600090505b91905056fea165627a7a72305820" + \
              "bfe3c81d3efc9ae914e9b066b06eb69525eb959f79f153fb851f4ef0c293d4280029"

    # program = "608060405234801561001057600080fd5b5060d18061001f6000396000f3fe" + \
    #           "6080604052600436106039576000357c010000000000000000000000000000" + \
    #           "000000000000000000000000000090048063a6c14f8d14603e575b600080fd" + \
    #           "5b348015604957600080fd5b50607360048036036020811015605e57600080" + \
    #           "fd5b81019080803590602001909291905050506089565b6040518082815260" + \
    #           "200191505060405180910390f35b60006005821415609b576001905060a056" + \
    #           "5b600090505b91905056fea165627a7a72305820bfe3c81d3efc9ae914e9b0" + \
    #           "66b06eb69525eb959f79f153fb851f4ef0c293d4280029"

    # contract branchTest {
    #   function renderAdd (int value) public pure returns (int) {
    #     if (value == 5) {
    #       return 1;
    #     } else {
    #       return 0;
    #     }
    #   }
    # }

    program = bytes.fromhex(program)

    machine = SpeculativeMachine(program)
    machine.concrete_execution = True
    #machine.deploy(program)
    machine.program = program
    funcArg = BitVec('funcArg', 256)

    arg1 = BitVec('arg1', 256)

    machine.inputs = [funcArg, arg1]
    #machine.inputs = [funcArg, (5).to_bytes(32, 'big')]

    machine.input = bytes()
    machine.concrete_execution = False
    machine.call_value = 0
    possible_machines = [machine]

    final_machines = []

    branches_evaluated = 0
    while len(possible_machines) > 0:
        branches_evaluated += 1
        machine = possible_machines.pop()
        try:
            machine.execute()
        except PathDivergenceException as e:
            error = e
            machines = error.possible_machines
            solvers = []
            for i, machine in enumerate(machines):
                print(i)
                solver = Solver()
                solver.add(*machine.path_conditions)
                solvers.append(solver)
                print(solver)
                print(solver.check())
                if solver.check() == sat:
                    possible_machines.append(machine)
                    print("POSSIBLE")
                else:
                    import pdb; pdb.set_trace()
                    print("NOT POSSIBLE")
            #         import pdb; pdb.set_trace()
            # raise Exception()
        except ReturnException as e:
            final_machines.append({
                'machine': machine,
                'type': e.func_type,
                'value': e.value,
                'path_conditions': machine.path_conditions
            })
            # print(e)
            # import pdb; pdb.set_trace()
            # pass
        except Exception as e:
            import pdb; pdb.set_trace()
            raise e
            pass
    print(final_machines)
    print(branches_evaluated)
    print("DONE")
    for i, machine in enumerate(final_machines):
        print('-------')
        print(i)
        solver = Solver()
        solver.add(*machine['path_conditions'])
        solvers.append(solver)
        print(machine['type'])
        print(machine['value'])
        print(solver)
        print(solver.check())
        if solver.check():
            print(solver.model())
        print(machine['machine'].print_state())
    raise Exception()
    import pdb; pdb.set_trace()
    pass
 #program = bytes.fromhex('6000355b6001900380600357')

    # 0      PUSH1  => 00
    # 2      CALLDATALOAD
    # 3      JUMPDEST
    # 4      PUSH1  => 01
    # 6      SWAP1
    # 7      SUB
    # 8      DUP1
    # 9      PUSH1  => 03
    # 11     JUMPI