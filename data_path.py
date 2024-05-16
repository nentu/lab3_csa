import json
import logging

from isa import Opcode, code_to_operation, operation_to_code


class HltError(Exception):
    pass


class EmptyBufferError(Exception):
    pass


class DataPath:
    acc = None
    reg_ip = None
    reg_ir = None
    reg_addr = None
    flag_z = None
    mux_addr_i = None
    mux_alu_i = None

    mux_jmp_type = None
    signals_dict = None

    data_mem = None
    instruct_mem = None

    data_mem_size = None
    instruct_mem_size = None
    input_buffer = None
    output_buffer = None

    def __init__(self, data_mem_size, instruct_mem_size, input_buffer):
        self.input_buffer = input_buffer
        self.output_buffer = list()

        self.ports = [
            {
                "in": list(),
                "out": list()
            }
            for i in range(2)]

        self.instruct_mem_size = instruct_mem_size
        self.data_mem_size = data_mem_size

        self.acc = 0
        self.reg_ip = 0
        self.reg_ir = 0
        self.reg_addr = 0
        self.flag_z = 0
        self.mux_addr_i = 0
        self.mux_alu_i = 0
        self.mux_alu_input_i = 0
        self.mux_ip_i = 0

        self.signals_dict = {
            "MUX_addr": [0, 0],
            "MUX_ALU": [0, 0],
            "MUX_ALU_input": [0, 0],
            "MUX_jmp_type": [0, 0],
            "MUX_ip": [0, 0],
            "reg_ip": self.reg_ip,
            "reg_ir": self.reg_ir,
            "reg_addr": self.reg_addr,
            "acc": self.acc,
            "z": self.flag_z,
            "ALU_instr": None,
            "data_mem_input": 0
        }
        self.data_mem = list()
        self.instruct_mem = list()

    def load_data_mem(self, mem_list: list):
        self.data_mem = mem_list + [0] * (self.data_mem_size - len(mem_list))

    def load_instr_mem(self, instr_list: list):
        self.instruct_mem = instr_list + [0] * (self.instruct_mem_size - len(instr_list))

    def get_instruction_signal(self):
        ip_reg = self.signals_dict["reg_ip"]
        instr = self.instruct_mem[ip_reg]
        code = operation_to_code(instr["opcode"], instr["address_type"])

        self.signals_dict["reg_ir"] = code
        self.signals_dict["ALU_instr"] = code
        self.signals_dict["MUX_addr"][1] = instr["arg"]
        self.signals_dict["MUX_ip"][0] = instr["arg"]
        self.signals_dict["MUX_ALU"][0] = instr["arg"]

    def _get_mux_alu_input(self):
        if self.mux_alu_input_i == 0:
            mux = self.signals_dict["MUX_ALU"][self.mux_alu_i]
        elif self.mux_alu_input_i == 1:
            if len(self.input_buffer) == 0:
                logging.warning("Input buffer is empty!")
                raise EmptyBufferError()
            mux = self.input_buffer.pop(0)
            logging.debug(f"input: {mux}")

        else:
            port_id = self.mux_alu_input_i - 2
            buffer = self.ports[port_id]["in"]
            if len(buffer) == 0:
                logging.debug(f"port buffer #{port_id} is empty")
                raise EmptyBufferError()
            mux = buffer.pop(0)
            logging.debug(f"input from port #{port_id}: {mux}")

        return mux

    def do_alu_signal(self, s=1):  # noqa: C901
        if s == 0:
            return
        instr = code_to_operation(self.signals_dict["ALU_instr"])[0]

        acc = self.acc
        mux = self._get_mux_alu_input()

        if instr == Opcode.INC:
            res = acc + 1
        elif instr == Opcode.DEC:
            res = acc - 1
        elif instr == Opcode.CLS:
            res = 0
        elif instr == Opcode.NEG:
            res = -acc
        elif instr == Opcode.ADD:
            res = acc + mux
        elif instr == Opcode.SUB:
            res = acc - mux
        elif instr in [Opcode.LOAD, Opcode.INPUT, Opcode.PORT1_IN, Opcode.PORT2_IN]:
            res = mux
        else:
            raise Exception("wrong ALU cmd {}".format(instr))  # noqa: TRY002

        self.signals_dict["acc"] = res
        self.signals_dict["z"] = res == 0

    def get_data_signal(self, s=1):
        if s == 0:
            return
        addr = self.signals_dict["reg_addr"]
        data = self.data_mem[addr]
        self.signals_dict["MUX_addr"][0] = data
        self.signals_dict["MUX_ALU"][1] = data

    def set_data_signal(self, s=1):
        if s == 0:
            return
        addr = self.signals_dict["reg_addr"]
        data = self.signals_dict["data_mem_input"]

        self.data_mem[addr] = data

    def latch_reg_ip_signal(self, s=1):
        if s == 0:
            return
        self.reg_ip = self.signals_dict["MUX_ip"][self.mux_ip_i]
        self.signals_dict["MUX_ip"][1] = self.reg_ip + 1
        self.signals_dict["reg_ip"] = self.reg_ip
        self.get_instruction_signal()

    def latch_reg_ir_signal(self, s=1):
        if s == 0:
            return
        self.reg_ir = self.signals_dict["reg_ir"]

        if code_to_operation(self.reg_ir)[0] == Opcode.HLT:
            raise HltError()

    def latch_reg_addr_signal(self, s=1):
        if s == 0:
            return
        self.reg_addr = self.signals_dict["MUX_addr"][self.mux_addr_i]
        self.signals_dict["reg_addr"] = self.reg_addr

    def set_mux_jmp_type(self, i):
        self.mux_jmp_type = i
        self.mux_ip_i = self.signals_dict["MUX_jmp_type"][i]

    def set_mux_ip_signal(self, i):
        self.signals_dict["MUX_jmp_type"][0] = i

    def set_mux_addr_signal(self, i):
        self.mux_addr_i = i

    def set_mux_alu_signal(self, i):
        self.mux_alu_i = i

    def set_mux_alu_input_signal(self, i):
        self.mux_alu_input_i = i

    def latch_acc_signal(self, s=1):
        if s == 0:
            return
        acc = self.signals_dict["acc"]
        self._latch_z_flag_signal()
        self.acc = acc

        self.signals_dict["MUX_ALU"][1] = acc
        self.signals_dict["data_mem_input"] = acc

    def _latch_z_flag_signal(self, s=1):
        if s == 0:
            return
        self.flag_z = self.signals_dict["z"]
        self.signals_dict["MUX_jmp_type"][1] = 1 - self.flag_z

    def output_signal(self, s=1):
        if s == 0:
            return
        logging.debug(f"Output: {self.output_buffer_to_text()} <= {self.acc}")
        self.output_buffer.append(self.acc)

    def port_1_signal(self, s=1):
        if s == 0:
            return
        self._port_signal(0)

    def port_2_signal(self, s=1):
        if s == 0:
            return
        self._port_signal(1)

    def _port_signal(self, i):
        self.ports[i]["out"].append(self.acc)

    def load_program(self, program_name):
        with open(program_name) as p:
            program = json.load(p)

        mem_list = list()
        for i in program["data"]:
            if i["size"] != 1:
                mem_list.append(i["size"])
            mem_list += i["init"]

        code_list = program["code"]

        self.load_data_mem(mem_list)
        self.load_instr_mem(code_list)

        return code_list, mem_list

    def output_buffer_to_text(self):
        res = list()
        for i in self.output_buffer:
            if ord(" ") <= i <= ord("z") or i == ord("\n"):
                res.append(chr(i))
            else:
                res.append(i)
        return res
