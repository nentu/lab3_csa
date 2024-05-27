"""
Here we define microcode blocks for each operation and addressing type.
We write id of activate bits. The first bit is 0
"""

from isa import Address, Opcode

bit_dict = {
    "IP": 0,
    "IM": 1,
    "MUX_IP": 2,
    "MUX_JMP_TYPE": 3,
    "IR": 4,
    "MUX_ADDR": 5,
    "ADDR": 6,
    "MUX_ALU": 7,
    "MUX_ALU_INPUT": 8,
    "ALU": 9,
    "ACC": 10,
    "OUTPUT": 11,
    "DIN": 12,  # data input
    "DOUT": 13,  # data output
    "M_MUX_IP": 14,
    "M_IP": 15,
    "M_IM": 16,
    "PORT1_OUT": 17,
    "PORT2_OUT": 18,
}

bit_dict["M_MUX_IP_2"] = -2

bit_dict["PORT1_IN"] = bit_dict["MUX_ALU_INPUT"]
bit_dict["PORT2_IN"] = bit_dict["MUX_ALU_INPUT"]

bit_dict["MUX_ADDR_S"] = bit_dict["MUX_ADDR"]
bit_dict["MUX_ALU_S"] = bit_dict["MUX_ALU"]
bit_dict["MUX_ALU_INPUT_S"] = bit_dict["MUX_ALU_INPUT"]
# -5 - don't change
SKIP_LIST = ["MUX_ADDR_S", "MUX_ALU_S", "MUX_ALU_INPUT_S"]


def get_line_len():
    return max(bit_dict.values()) + 1


START = [["IP", "IR", "IM"] + ["M_MUX_IP_2", "M_IP", "M_IM"]]

# Command implementation
# На этом момента на левый вход АЛУ уже подаётся нужный аргумент и адрес операнда находится в регистре AR

ALU_OPERATION = [  # inc, dec, add, sub, cls, neg, load
    ["MUX_IP", "ALU", "ACC"]
]

STORE = [["MUX_IP", "DIN"]]

JMP = [[]]

JMPZ = [["MUX_JMP_TYPE"]]

INPUT = [["MUX_IP", "MUX_ALU_INPUT", "ALU", "ACC"] + ["MUX_ADDR_S", "MUX_ALU_S"]]
PORT1_IN = [["MUX_IP", "PORT1_IN", "ALU", "ACC"]]
PORT2_IN = [["MUX_IP", "PORT2_IN", "ALU", "ACC"]]

OUTPUT = [["MUX_IP", "OUTPUT"]]

PORT1_OUT = [["MUX_IP", "PORT1_OUT"]]
PORT2_OUT = [["MUX_IP", "PORT2_OUT"]]

HLT = []

op_dict = {
    Opcode.INC: ALU_OPERATION.copy(),
    Opcode.DEC: ALU_OPERATION.copy(),
    Opcode.CLS: ALU_OPERATION.copy(),
    Opcode.NEG: ALU_OPERATION.copy(),
    Opcode.HLT: HLT.copy(),
    Opcode.INPUT: INPUT.copy(),
    Opcode.OUTPUT: OUTPUT.copy(),
    Opcode.LOAD: ALU_OPERATION.copy(),
    Opcode.STORE: STORE.copy(),
    Opcode.ADD: ALU_OPERATION.copy(),
    Opcode.SUB: ALU_OPERATION.copy(),
    Opcode.JMP: JMP.copy(),
    Opcode.JMPZ: JMPZ.copy(),
    Opcode.PORT1_IN: PORT1_IN.copy(),
    Opcode.PORT2_IN: PORT2_IN.copy(),
    Opcode.PORT1_OUT: PORT1_OUT.copy(),
    Opcode.PORT2_OUT: PORT2_OUT.copy(),
}

#  Address implementation
# После выполнения на левом входе АЛУ должен быть аргумент и в ADR его адрес

DIR_ADDR = []

VAL = [["MUX_ALU", "MUX_ADDR", "ADDR", "DOUT"]]

INDIR = [
    ["MUX_ADDR", "ADDR", "DOUT"],
    ["ADDR", "DOUT", "MUX_ALU"],
]

NO_OP = []

address_dict = {
    Address.NO_OP: NO_OP,
    Address.DIRECT: DIR_ADDR,
    Address.LABEL_ADDR: DIR_ADDR,
    Address.LABEL_VAL: VAL,
    Address.INDIRECT: INDIR,
}

for name, operation in op_dict.items():
    if name == HLT:
        continue
    for i in range(len(operation)):
        if i != len(operation) - 1:
            operation[i] += ["M_MUX_IP"]
        operation[i] += ["M_IP", "M_IM"]

        if name != Opcode.INPUT:
            operation[i] += SKIP_LIST

for address in address_dict.values():
    for i in range(len(address)):
        address[i] += ["M_MUX_IP", "M_IP", "M_IM"]


