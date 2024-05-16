from __future__ import annotations

from typing import Any

from isa import Address, Opcode, allowed_addressing, operation_to_code
from mc_consts import SKIP_LIST, START, address_dict, bit_dict, get_line_len, op_dict


def generate_mc() -> tuple[list[Any], dict[tuple[Any, Any], int]]:
    res = list()

    start_ids = dict()
    res += _labels_to_bits(START)
    for instr, addr_list in allowed_addressing.items():
        for addr in addr_list:
            start_ids[operation_to_code(instr, addr)] = len(res)
            res.extend(_generate_block(instr, addr))

    return res, start_ids


def _generate_block(instr, addr, printed=False):
    return _labels_to_bits(_generate_block_symbols(instr, addr, printed=printed))


def _generate_block_symbols(instr, addr, printed=False):
    if printed:
        print(address_dict[addr])
        print(op_dict[instr])

    res = list()
    res += address_dict[addr]
    operation = op_dict[instr]
    res += operation
    return res


def _labels_to_bits(code: list):  # noqa: C901
    res = list()
    for i in range(len(code)):
        line = [0] * get_line_len()
        for j in code[i]:
            bin_code = bit_dict[j]
            if bin_code >= 0:
                line[bin_code] = 1

        for skip_label in SKIP_LIST:
            if skip_label in code[i]:
                line[bit_dict[skip_label]] = 0 if len(res) == 0 else res[-1][bit_dict[skip_label]]
        if "M_MUX_IP_2" in code[i]:
            line[bit_dict["M_MUX_IP"]] = 2
        if "PORT1_IN" in code[i]:
            line[bit_dict["PORT1_IN"]] = 2
        if "PORT2_IN" in code[i]:
            line[bit_dict["PORT2_IN"]] = 3

        res.append(line)
    return res


if __name__ == "__main__":
    res = _labels_to_bits(_generate_block_symbols(Opcode.OUTPUT, Address.NO_OP, True))

    for line in res:
        print("", end="[")
        for j, bit in enumerate(line):
            if bit != 0:
                print(j, end=" ")
        print("]")
