from enum import StrEnum


class Address(StrEnum):
    NO_OP = "no_op"
    DIRECT = "direct_addr"
    LABEL_ADDR = "label_addr"
    LABEL_VAL = "label_val"
    INDIRECT = "indirect_addr"


class Opcode(StrEnum):
    INC = "inc"  # acc operations
    DEC = "dec"
    CLS = "cls"
    NEG = "neg"

    ADD = "add"  # + and -
    SUB = "sub"

    INPUT = "input"  # io operations
    OUTPUT = "output"

    LOAD = "load"  # memory operations
    STORE = "store"

    JMP = "jmp"  # move operations
    JMPZ = "jmpz"

    HLT = "hlt"  # stop

    PORT1_OUT = "port1_out"
    PORT1_IN = "port1_in"
    PORT2_OUT = "port2_out"
    PORT2_IN = "port2_in"


def code_to_operation(op_id: int):
    return opcode_list[op_id // 10], address_list[op_id % 10]


def operation_to_code(operation: Opcode, address: Address):
    return opcode_list.index(operation) * 10 + address_list.index(address)


opcode_list = [
    Opcode.INC,
    Opcode.DEC,
    Opcode.CLS,
    Opcode.NEG,
    Opcode.ADD,
    Opcode.SUB,
    Opcode.INPUT,
    Opcode.OUTPUT,
    Opcode.LOAD,
    Opcode.STORE,
    Opcode.JMP,
    Opcode.JMPZ,
    Opcode.HLT,
    Opcode.PORT1_OUT,
    Opcode.PORT2_OUT,
    Opcode.PORT1_IN,
    Opcode.PORT2_IN,
]

address_list = [
    Address.NO_OP,
    Address.DIRECT,
    Address.LABEL_ADDR,
    Address.LABEL_VAL,
    Address.INDIRECT,
]

allowed_addressing = {
    Opcode.INC: [Address.NO_OP],
    Opcode.DEC: [Address.NO_OP],
    Opcode.CLS: [Address.NO_OP],
    Opcode.NEG: [Address.NO_OP],
    Opcode.HLT: [Address.NO_OP],
    Opcode.INPUT: [Address.NO_OP],
    Opcode.PORT1_IN: [Address.NO_OP],
    Opcode.PORT2_IN: [Address.NO_OP],
    Opcode.OUTPUT: [Address.NO_OP],
    Opcode.PORT1_OUT: [Address.NO_OP],
    Opcode.PORT2_OUT: [Address.NO_OP],
    Opcode.LOAD: [Address.DIRECT, Address.LABEL_VAL, Address.LABEL_ADDR, Address.INDIRECT],
    Opcode.STORE: [Address.LABEL_VAL, Address.INDIRECT],
    Opcode.ADD: [Address.LABEL_VAL, Address.DIRECT],
    Opcode.SUB: [Address.LABEL_VAL, Address.DIRECT],
    Opcode.JMP: [Address.LABEL_VAL],
    Opcode.JMPZ: [Address.LABEL_VAL],
}
