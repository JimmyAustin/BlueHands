import json

opcodes = json.load(open('opcodes/evm_opcodes/all_opcodes.json'))

opcodes_by_bin = {bytes.fromhex(x['bin']): x for x in opcodes}


def relevant_opcode_details(opcode):
    if opcode in opcodes_by_bin:
        return opcodes_by_bin[opcode]
    else:
        raise ValueError(f"Unknown Opcode: {opcode}")
