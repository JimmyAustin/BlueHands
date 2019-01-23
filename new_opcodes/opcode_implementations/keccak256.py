import sha3
from utils import value_is_constant, bytes_to_uint
from z3 import IntSort, Const, If, BitVecSort, Or

def keccak256_op(execution_context, contract, universe):
    address = execution_context.stack.pop()
    length = execution_context.stack.pop()
    memory_value = contract.memory.get(address, length)
    if value_is_constant(memory_value):
        k = sha3.keccak_256()
        k.update(memory_value)
        digest = k.digest()
        universe.seen_hashes[bytes(memory_value)] = digest
        print("Throwing hash")
        print(universe.seen_hashes)
        execution_context.stack.push(digest)
    else:
        result = Const(False, BitVecSort(256))

        for k, v in universe.seen_hashes.items():
            #if len(k) == memory_value.size():
            result = If(memory_value == bytes_to_uint(k), bytes_to_uint(v), result)
        orSet = Or([memory_value == bytes_to_uint(k) for k in universe.seen_hashes.keys()])
        universe.path_conditions.append(orSet)
        execution_context.stack.push(result)

# class Keccak256Opcode(Opcode):
#     def __init__(self, instruction):
#         super().__init__(instruction)

#     def execute(self, machine):
#         address = machine.stack.pop()
#         length = machine.stack.pop()
#         memory_value = machine.memory.get(address, length)
#         if value_is_constant(memory_value):
#             k = sha3.keccak_256()
#             k.update(memory_value)
#             digest = k.digest()
#             machine.hash_map[bytes(memory_value)] = digest
#             print("Throwing hash")
#             print(machine.hash_map)
#             machine.stack.push(digest)
#         else:
#             result = Const(False, BitVecSort(256))

#             for k, v in machine.hash_map.items():
#                 #if len(k) == memory_value.size():
#                 result = If(memory_value == bytes_to_uint(k), bytes_to_uint(v), result)
#             orSet = Or([memory_value == bytes_to_uint(k) for k in machine.hash_map.keys()])
#             machine.path_conditions.append(orSet)
#             machine.stack.push(result)

#             # if memory_value.size() == 256:
#             #     import pdb; pdb.set_trace()
#             #     raise Exception('Invalid stuff')
#             #     machine.stack.push(memory_value)                
#             # else:
#             #     raise NotImplementedError('Cant hash symbols not of bitvec size 256')
