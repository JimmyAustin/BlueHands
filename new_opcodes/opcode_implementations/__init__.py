# flake8: noqa

def tempadwawdawdawdawd(execution_context, contract, universe):
    execution_context.stack.push(execution_context.get_next_program_bytes(length))

def get_push_op_func(length):
    def push(execution_context, contract, universe):
        execution_context.stack.push(execution_context.get_next_program_bytes(length))
    return push

def get_dup_op_func(length):
    def dup(execution_context, contract, universe):
        execution_context.stack.push(execution_context.stack.stack[-length])
    return dup

def get_swap_op_func(length):
    def swap(execution_context, contract, universe):
        top_value = execution_context.stack.stack[-1]
        execution_context.stack.stack[-1] = execution_context.stack.stack[-(length + 1)]
        execution_context.stack.stack[-(length + 1)] = top_value
    return swap

from .stop import stop_op
from .add import add_op
from .mul import mul_op
from .sub import sub_op
from .div import div_op
# from .sdiv import sdiv_op
# from .mod import mod_op
# from .smod import smod_op
# from .addmod import addmod_op
# from .mulmod import mulmod_op
from .exp import exp_op
# from .signextend import signextend_op
from .lt import lt_op
from .gt import gt_op
# from .slt import slt_op
# from .sgt import sgt_op
from .eq import eq_op
from .iszero import iszero_op
from .and_code import and_op
from .or_code import or_op
# from .xor import xor_op
from .not_code import not_op
# from .byte import byte_op
# from .shl import shl_op
# from .shr import shr_op
# from .sar import sar_op
# from .rol import rol_op
# from .ror import ror_op
from .keccak256 import keccak256_op
# from .address import address_op
# from .balance import balance_op
# from .origin import origin_op
from .caller import caller_op
from .callvalue import callvalue_op
from .calldataload import calldataload_op
from .calldatasize import calldatasize_op
# from .calldatacopy import calldatacopy_op
# from .codesize import codesize_op
from .codecopy import codecopy_op
# from .gasprice import gasprice_op
# from .extcodesize import extcodesize_op
# from .extcodecopy import extcodecopy_op
# from .blockhash import blockhash_op
# from .coinbase import coinbase_op
from .timestamp import timestamp_op
# from .number import number_op
# from .difficulty import difficulty_op
# from .gaslimit import gaslimit_op
from .pop import pop_op
from .mload import mload_op
from .mstore import mstore_op
# from .mstore8 import mstore8_op
from .sload import sload_op
from .sstore import sstore_op
# from .swap import swap_op
from .jump import jump_op
from .jumpi import jumpi_op
# from .pc import pc_op
# from .msize import msize_op
from .gas import gas_op
from .jumpdest import jumpdest_op
# from .create import create_op
from .call import call_op
# from .callcode import callcode_op
from .return_code import return_op
# from .delegatecall import delegatecall_op
# from .staticcall import staticcall_op
from .revert import revert_op
# from .selfdestruct import selfdestruct_op
# from .push import push_op
# from .dup import dup_op
# from .log import log_op

from .return_data_size import return_data_size_op
# from .return_data_copy import return_data_copy_op
