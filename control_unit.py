import logging
import sys

from data_path import DataPath, EmptyBufferError, HltError
from isa import code_to_operation
from mc_generator import generate_mc


class TickLimitError(Exception):
    pass


TICK_LIMIT = 5e4


class ControlUnit:
    mc_mem = None

    reg_ip = None
    mux = None
    jmp_mux_signal = None
    jmp_mux = (None, None)
    current_instr = None
    bits_func = None
    decode_dict = None

    def __init__(self, dp: DataPath, need_log=False):
        self.jmp = None
        self.need_log = need_log
        self.dp = dp

        self.mc_mem = []
        self.reg_ip = 0
        self.current_instr = None
        self.decode_dict = {}

        self.cmd_count = 0

        self.bits_func = [
            dp.latch_reg_ip_signal,
            dp.get_instruction_signal,
            dp.set_mux_ip_signal,
            dp.set_mux_jmp_type,
            dp.latch_reg_ir_signal,
            dp.set_mux_addr_signal,
            dp.latch_reg_addr_signal,
            dp.set_mux_alu_signal,
            dp.set_mux_alu_input_signal,
            dp.do_alu_signal,
            dp.latch_acc_signal,
            dp.output_signal,
            dp.set_data_signal,
            dp.get_data_signal,
            self.set_mux,
            self.latch_ip,
            self.get_mc_instruction_signal,
            dp.port_1_signal,
            dp.port_2_signal,
        ]

        self.load_mem()

        self.set_mux(0)
        self.latch_ip()
        self.get_mc_instruction_signal()

    def set_jmp_mux(self, signal):
        self.jmp = signal

    def set_mux(self, signal):
        self.mux = signal

        if signal == 0 and self.need_log:
            self.log_state()

    def latch_ip(self, signal=1):
        if signal != 1:
            return
        if self.mux == 0:
            self.reg_ip = 0
            self.cmd_count += 1
        elif self.mux == 1:
            self.reg_ip += 1
        elif self.mux == 2:
            self.reg_ip = self.decode()

    def get_mc_instruction_signal(self, s=1):
        if s == 0:
            return
        self.current_instr = self.mc_mem[self.reg_ip]

    def juggernaut(self):
        tick = 0
        while True:
            try:
                self.execute()
                tick += 1
            except HltError:
                break
            except EmptyBufferError:
                break

            if tick > TICK_LIMIT:
                logging.error("Tick limit exceeded")
                return -1
        return tick

    def execute(self):
        cmd = self.current_instr
        for bit, func in zip(cmd, self.bits_func):
            # if func == self.get_mc_instruction_signal:
            #     pass
            func(bit)

    def decode(self):
        return self.decode_dict[self.dp.reg_ir]

    def load_mem(self):
        self.mc_mem, self.decode_dict = generate_mc()

    def log_state(self):
        cmd, addr = (i.name for i in code_to_operation(self.dp.reg_ir))
        logging.debug(
            f"IP: {self.dp.reg_ip}; "
            f"IR: cmd: {cmd}, addr {addr}; "
            f"ADDR: {self.dp.reg_addr}; "
            f"Z: {self.dp.flag_z}; "
            f"ACC: {self.dp.acc}"
        )


def get_input_list(input_text):
    res_list = list()
    for input_text in input_text.split():
        res = list()
        for i in list(input_text):
            if i.isdigit():
                res.append(int(i))
            else:
                res.append(ord(i))
        res_list.append(res)

    while len(res_list) < 3:
        res_list.append([])

    return res_list


def main(scr_name, input_name):
    with open(input_name) as input_name:
        input_b, port1_b, port2_b = get_input_list(input_name.read())

    dp = DataPath(128, 128, input_b)
    dp.load_program(scr_name)

    dp.ports[0]["in"] = port1_b
    dp.ports[1]["in"] = port2_b

    cu = ControlUnit(dp, True)

    tick_count = cu.juggernaut()
    cmd_count = cu.cmd_count

    output = cu.dp.output_buffer + cu.dp.ports[0]["out"] + cu.dp.ports[1]["out"]

    for i in output:
        if ord(" ") <= i <= ord("z") or i == ord("\n"):
            print(chr(i), end="")
        else:
            print(i, end="")

    print(f"\n\nTick count: {tick_count}, Command count: {cmd_count}")


if __name__ == "__main__":
    source_file, input_file = sys.argv[1:]
    main(source_file, input_file)
