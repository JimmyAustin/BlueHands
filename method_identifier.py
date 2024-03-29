from z3 import BoolRef, ArithRef, BitVecRef
from utils import uint_to_bytes, information_for_function_sig


def identify_methods(machine):
    method_calls = []
    for path_condition in machine.path_conditions:
        try:
            func_sig = identify_path_conditions(path_condition)
        except ValueError:
            func_sig = None
        if func_sig is None:
            continue
        method_calls.append(information_for_function_sig(func_sig)['name'])
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


