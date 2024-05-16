"""
Here we define microcode blocks for each operation and addressing type.
We write id of activate bits. The first bit is 0
"""

from isa import Address, Opcode

bit_dict = {
    "IP": 0,
    "MUX_IP": 1,
    "MUX_JMP_TYPE": 2,
    "IR": 3,
    "MUX_ADDR": 4,
    "ADDR": 5,
    "MUX_ALU": 6,
    "MUX_ALU_INPUT": 7,
    "ALU": 8,
    "ACC": 9,
    "OUTPUT": 10,
    "DIN": 11,
    "DOUT": 12,
    "M_MUX_IP": 13,
    "M_IP": 14,
    "PORT1_OUT": 15,
    "PORT2_OUT": 16,
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


START = [
    ["IP", "IR"] + ["M_MUX_IP_2", "M_IP"]
]

# Command implementation
# На этом момента на левый вход АЛУ уже подаётся нужный аргумент и адрес операнда находится в регистре AR

ALU_OPERATION = [  # inc, dec, add, sub, cls, neg, load
    ["MUX_IP", "ALU", "ACC"] + ["M_IP"] + SKIP_LIST
]


STORE = [
    ["MUX_IP", "DIN"] + ["M_IP"] + SKIP_LIST
]

JMP = [
    ["M_IP"] + SKIP_LIST
]

JMPZ = [
    ["MUX_JMP_TYPE"] + ["M_IP"] + SKIP_LIST
]

INPUT = [
    ["MUX_IP", "MUX_ALU_INPUT", "ALU", "ACC"] + ["M_IP"] + ["MUX_ADDR_S", "MUX_ALU_S"]
]
PORT1_IN = [
    ["MUX_IP", "PORT1_IN", "ALU", "ACC"] + ["M_IP"] + SKIP_LIST
]
PORT2_IN = [
    ["MUX_IP", "PORT2_IN", "ALU", "ACC"] + ["M_IP"] + SKIP_LIST
]

OUTPUT = [
    ["MUX_IP", "OUTPUT"] + ["M_IP"] + SKIP_LIST
]

PORT1_OUT = [
    ["MUX_IP", "PORT1_OUT"] + ["M_IP"] + SKIP_LIST
]
PORT2_OUT = [
    ["MUX_IP", "PORT2_OUT"] + ["M_IP"] + SKIP_LIST
]

HLT = []

op_dict = {
    Opcode.INC: ALU_OPERATION,
    Opcode.DEC: ALU_OPERATION,
    Opcode.CLS: ALU_OPERATION,
    Opcode.NEG: ALU_OPERATION,
    Opcode.HLT: HLT,
    Opcode.INPUT: INPUT,
    Opcode.OUTPUT: OUTPUT,
    Opcode.LOAD: ALU_OPERATION,
    Opcode.STORE: STORE,
    Opcode.ADD: ALU_OPERATION,
    Opcode.SUB: ALU_OPERATION,
    Opcode.JMP: JMP,
    Opcode.JMPZ: JMPZ,
    Opcode.PORT1_IN: PORT1_IN,
    Opcode.PORT2_IN: PORT2_IN,
    Opcode.PORT1_OUT: PORT1_OUT,
    Opcode.PORT2_OUT: PORT2_OUT,
}

#  Address implementation
# После выполнения на левом входе АЛУ должен быть аргумент и в ADR его адрес

DIR_ADDR = [
]

VAL = [
    ["MUX_ALU", "MUX_ADDR", "ADDR", "DOUT"] + ["M_MUX_IP", "M_IP"]
]

INDIR = [
    ["MUX_ADDR", "ADDR", "DOUT"] + ["M_MUX_IP", "M_IP"],
    ["ADDR", "DOUT", "MUX_ALU"] + ["M_MUX_IP", "M_IP"]
]

NO_OP = []

address_dict = {
    Address.NO_OP: NO_OP,
    Address.DIRECT: DIR_ADDR,
    Address.LABEL_ADDR: DIR_ADDR,
    Address.LABEL_VAL: VAL,
    Address.INDIRECT: INDIR,
}

if __name__ == "__main__":
    print(get_line_len())
