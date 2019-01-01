from z3 import BoolRef, ArithRef, BitVecRef
from utils import uint_to_bytes


def identify_methods(machine):
    method_calls = []
    for path_condition in machine.path_conditions:
        func_sig = identify_path_conditions(path_condition)
        if func_sig is None:
            continue
        method_calls.append(name_for_function_sig(func_sig))
    return method_calls


# Path conditons look something like this
# If(UDiv(input_0_0,
#         26959946667150639794667015087019630673637144422540572481103610249216) ==
#    3504541104,
#    1,
#    0) !=
# 0

def identify_path_conditions(path_condition):
    if path_condition.__class__ != BoolRef:
        return None

    if path_condition.decl().name() != 'distinct': # Todo: Find something better then this
        return None

    children = path_condition.children()
    if children[1].params()[0] != '0':
        return None

    if_statement = children[0]
    if_statement_children = if_statement.children()

    if len(if_statement_children) != 3:
        return None

    if if_statement_children[1].params()[0] != '1' or if_statement_children[2].params()[0] != '0':
        return None
    
    div_compr_statement = if_statement_children[0]
    if div_compr_statement.__class__ != BoolRef:
        return None

    children = div_compr_statement.children()
    input_symbol = children[0]
    method_comp = children[1]

    if input_symbol.__class__ != BitVecRef:
        return None

    input_children = input_symbol.children()
    if len(input_children) == 0:
        return None

    if str(input_children[0]).startswith('input_') == False:
        return None

    function_sig = uint_to_bytes(int(method_comp.params()[0])).hex()[56:]
    #import pdb; pdb.set_trace()

    if len(function_sig) != 8:
        return None
    return function_sig


def name_for_function_sig(sig):
    return {
        '3fb2a74e': 'cfoWithdraw(address,uint256)',
        'd0e30db0': 'deposit()',
        '4e0a3379': 'setCFO(address)',
        '2e1a7d4d': 'withdraw(uint256)',
        '846719e0': 'get(int256)',
        'e5c19b2d': 'set(int256)',
        'a5f3c23b': 'add(int256,int256)',
        '7e62eab8': 'withdraw(int256)',
        '6d4ce63c': 'get()',
        'ad065eb5': 'canIdentifySender(address)',
    }.get(sig, f"Unknown Method: {sig}")
