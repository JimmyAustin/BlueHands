# flake8: noqa

from .opcode import Opcode
from .opcode_implementations import *

from .evm_opcodes.opcodes import opcodes_by_bin
from .invalid_opcode import InvalidOpcode


class OpcodeBuilder:
    def build(instruction):
        if instruction not in opcode_bin_to_text_mapping:
            return InvalidOpcode(instruction)
        text = opcode_bin_to_text_mapping[instruction]
        class_to_init, additional_args = directory[text]
        return class_to_init(instruction, *additional_args)

    def instruction_is_implemented(text):
        class_to_init, additional_args = directory[text]
        return class_to_init != Opcode

directory = {
    "STOP": (StopOpcode, []),
    "ADD": (AddOpcode, []),
    "MUL": (MulOpcode, []),
    "SUB": (SubOpcode, []),
    "DIV": (DivOpcode, []),
    "SDIV": (SdivOpcode, []),
    "MOD": (ModOpcode, []),
    "SMOD": (SmodOpcode, []),
    "ADDMOD": (AddmodOpcode, []),
    "MULMOD": (MulmodOpcode, []),
    "EXP": (ExpOpcode, []),
    "SIGNEXTEND": (SignextendOpcode, []),
    "LT": (LtOpcode, []),
    "GT": (GtOpcode, []),
    "SLT": (SltOpcode, []),
    "SGT": (SgtOpcode, []),
    "EQ": (EqOpcode, []),
    "ISZERO": (IszeroOpcode, []),
    "AND": (AndOpcode, []),
    "OR": (OrOpcode, []),
    "XOR": (XorOpcode, []),
    "NOT": (NotOpcode, []),
    "BYTE": (ByteOpcode, []),
    "SHL": (ShlOpcode, []),
    "SHR": (ShrOpcode, []),
    "SAR": (SarOpcode, []),
    "ROL": (RolOpcode, []),
    "ROR": (RorOpcode, []),
    "KECCAK256": (Keccak256Opcode, []),
    "ADDRESS": (AddressOpcode, []),
    "BALANCE": (BalanceOpcode, []),
    "ORIGIN": (OriginOpcode, []),
    "CALLER": (CallerOpcode, []),
    "CALLVALUE": (CallValueOpcode, []),
    "CALLDATALOAD": (CalldataloadOpcode, []),
    "CALLDATASIZE": (CalldatasizeOpcode, []),
    "CALLDATACOPY": (CalldatacopyOpcode, []),
    "CODESIZE": (CodesizeOpcode, []),
    "CODECOPY": (CodecopyOpcode, []),
    "GASPRICE": (GaspriceOpcode, []),
    "EXTCODESIZE": (ExtcodesizeOpcode, []),
    "EXTCODECOPY": (ExtcodecopyOpcode, []),
    "BLOCKHASH": (BlockhashOpcode, []),
    "COINBASE": (CoinbaseOpcode, []),
    "TIMESTAMP": (TimestampOpcode, []),
    "NUMBER": (NumberOpcode, []),
    "DIFFICULTY": (DifficultyOpcode, []),
    "GASLIMIT": (GaslimitOpcode, []),
    "POP": (PopOpcode, []),
    "MLOAD": (MloadOpcode, []),
    "MSTORE": (MstoreOpcode, []),
    "MSTORE8": (Mstore8Opcode, []),
    "SLOAD": (SloadOpcode, []),
    "SSTORE": (SstoreOpcode, []),
    "JUMP": (JumpOpcode, []),
    "JUMPI": (JumpiOpcode, []),
    "PC": (PcOpcode, []),
    "MSIZE": (MsizeOpcode, []),
    "GAS": (GasOpcode, []),
    "JUMPDEST": (JumpdestOpcode, []),
    "CREATE": (CreateOpcode, []),
    "CALL": (CallOpcode, []),
    "CALLCODE": (CallcodeOpcode, []),
    "RETURN": (ReturnOpcode, []),
    "DELEGATECALL": (DelegatecallOpcode, []),
    "STATICCALL": (StaticcallOpcode, []),
    "REVERT": (RevertOpcode, []),
    "SELFDESTRUCT": (SelfdestructOpcode, []),
    "RETURNDATASIZE": (ReturnDataSizeOpcode, []),
    "RETURNDATACOPY": (ReturnDataCopyOpcode, []),
}

for i in range(33):
    directory[f"PUSH{i}"] = (PushOpcode, [i])
for i in range(17):
    directory[f"SWAP{i}"] = (SwapOpcode, [i])
for i in range(17):
    directory[f"DUP{i}"] = (DupOpcode, [i])
for i in range(5):
    directory[f"LOG{i}"] = (LogOpcode, [i])

opcode_bin_to_text_mapping = {k: v['text'] for k, v in opcodes_by_bin.items()}
