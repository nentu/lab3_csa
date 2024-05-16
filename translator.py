import json
import sys

from isa import Address, Opcode, allowed_addressing


def _print_string(str_list):
    for i in str_list:
        print(chr(i))


class InvalidCodeError(Exception):
    def __init__(self, too_many_symbol, data_line):
        super().__init__(f'Invalid code: too many "{too_many_symbol}" in  "{data_line}"')


class Translator:
    data = None
    code = None
    text = None

    data_labels = None
    code_labels = None

    def __init__(self, filename):
        with open(filename) as f:
            self.text = f.readlines()

        self.data = list()
        self.code = list()

        self.data_labels = dict()
        self.code_labels = dict()

    def _clean_code(self):
        """
        remove comments, empty lines and strip lines

        """

        new_text = list()

        for i in self.text:
            i = i.split("//")[0]
            i = i.strip()
            i = i.replace("'", '"')
            i = i.replace("inp 0x1", "port1_in")
            i = i.replace("inp 0x2", "port2_in")
            i = i.replace("outp 0x1", "port1_out")
            i = i.replace("outp 0x2", "port2_out")
            if i != "":
                new_text.append(i)

        self.text = new_text

    def first_stage(self):  # noqa: C901
        """
        first stage:
            clean up code text
            fill data and code dicts,
            save labels
        :return:
        """

        data_place = 0
        instruct_place = 0

        self._clean_code()

        i = 0
        while i < len(self.text):
            data_line = self.text[i]

            if data_line == "section .data":
                i += 1
                continue
            if data_line == "section .code":
                i += 1
                break

            if data_line.count(":") > 1:
                raise InvalidCodeError(":", data_line)

            if data_line.count(":") == 1:
                label, data_line = data_line.split(":")
                data_line = data_line.strip()
                self.data_labels[label] = data_place

            if data_line[-1] == '"':  # string
                data_line = [ord(i) for i in data_line[1:-1]]

            elif data_line[-1] == ")":  # reserve mem
                symbols_num = int(data_line[1:-1])
                data_line = [0] * symbols_num
            elif data_line[:2] == "0x":
                data_line = [int(data_line[2:])]
                data_place -= 1

            self.data.append({"size": len(data_line), "init": list(data_line), "scr_line": i})

            data_place += len(data_line) + 1

            i += 1

        while i < len(self.text):
            instr_line = self.text[i]

            if instr_line.count(":") > 1:
                raise InvalidCodeError(":", data_line)

            if instr_line.count(":") == 1:
                label, instr_line = instr_line.split(":")
                instr_line = instr_line.strip()
                self.code_labels[label] = instruct_place
            if instr_line.count(" ") > 1:
                raise InvalidCodeError(" ", data_line)  # noqa: TRY003

            op = 0
            address_type = Address.NO_OP

            if instr_line.count(" ") == 1:
                instr_line, op = instr_line.split(" ")
                if op[:2] == "0x":
                    address_type = Address.DIRECT
                    op = int(op[2:])
                elif op[0] == "&":
                    address_type = Address.LABEL_ADDR
                    op = op[1:]
                elif op[0] == "(":
                    address_type = Address.INDIRECT
                    op = op[1:-1]
                else:
                    address_type = Address.LABEL_VAL
                    op = op

            instr = Opcode(instr_line)

            self.code.append({"opcode": instr, "arg": op, "address_type": address_type, "term": [i, instr]})

            instruct_place += 1

            i += 1

    def second_stage(self):
        """
        Replace labels with memory addresses
        """

        for i in range(len(self.code)):
            instr = self.code[i]

            addr_type = instr["address_type"]
            arg = instr["arg"]
            if addr_type not in allowed_addressing[instr["opcode"]]:
                raise Exception(f"Invalid address type for instruction: {instr['opcode']}")  # noqa: TRY002, TRY003

            if addr_type not in [Address.LABEL_ADDR, Address.LABEL_VAL, Address.INDIRECT]:
                continue

            if instr["opcode"] in [Opcode.JMP, Opcode.JMPZ]:
                if arg not in self.code_labels.keys():
                    raise Exception(f"No code label: {arg}")  # noqa: TRY002, TRY003
                instr["arg"] = self.code_labels[arg]
                continue

            if arg not in self.data_labels.keys():
                raise Exception(f"No data label: {arg}")  # noqa: TRY002, TRY003
            instr["arg"] = self.data_labels[arg]

    def translate(self, target, args=None):
        # TODO create ability to save cleaned code
        self.first_stage()
        self.second_stage()

        json_text = json.dumps({"data": self.data, "code": self.code})

        f = open(target, "w")
        f.write(json_text)
        f.close()

        return target


def main(source_file, target_file):
    tr = Translator(source_file)
    tr.translate(target_file)


if __name__ == "__main__":
    source_file, target_file = sys.argv[1:]
    main(source_file, target_file)
