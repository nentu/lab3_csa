import logging
import sys

from data_path import DataPath, EmptyBufferError, HltError
from isa import code_to_operation
from mc_generator import generate_mc


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
            dp.port_1_signal,
            dp.port_2_signal,
        ]

        self.load_mem()

        self.set_mux(0)
        self.latch_ip()

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
        self.get_instruction()

    def get_instruction(self):
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
        return tick

    def execute(self):
        cmd = self.current_instr
        for bit, func in zip(cmd, self.bits_func):
            if bit:
                func(bit)
            else:
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
    res = list()
    for i in list(input_text):
        if i.isdigit():
            res.append(int(i))
        else:
            res.append(ord(i))
    return res


def main(scr_name, input_name):
    with open(input_name) as input_name:
        chr_list = get_input_list(input_name.read())

    dp = DataPath(128, 128, chr_list)
    dp.load_program(scr_name)

    cu = ControlUnit(dp, True)

    tick_count = cu.juggernaut()
    cmd_count = cu.cmd_count

    output = cu.dp.output_buffer

    for i in output:
        if ord(" ") <= i <= ord("z") or i == ord("\n"):
            print(chr(i), end="")
        else:
            print(i)

    print(f"\n\nTick count: {tick_count}, Command count: {cmd_count}")


if __name__ == "__main__":
    source_file, input_file = sys.argv[1:]
    main(source_file, input_file)
