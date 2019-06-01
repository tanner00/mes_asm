import sys
import math
import re

def die(string):
    sys.stderr.write('\033[31;1;1m[death]\033[0m ' + string)
    sys.exit(1)

def die_if(condition, string):
    if condition:
        sys.stderr.write('\033[31;1;1m[death]\033[0m ' + string)
        sys.exit(1)

ID_REGEX = "[_A-Za-z][_a-zA-Z0-9]*$"

REGISTERS = ['$r' + str(i) for i in range (0, 32)]

INSTR_TO_OPCODE = {
    'nop': 0b000000,
    'movi': 0b000001,
    'movr': 0b000010,
    'load': 0b000011,
    'str': 0b000100,
    'add': 0b000101,
    'addi': 0b000110,
    'sub': 0b000111,
    'subi': 0b001000,
    'mul': 0b001001,
    'muli': 0b001010,
    'and': 0b001011,
    'andi': 0b001100,
    'or': 0b001101,
    'ori': 0b001110,
    'xor': 0b001111,
    'xori': 0b010000,
    'not': 0b010001,
    'sll': 0b010010,
    'srl': 0b010011,
    'jmp': 0b010100,
    'jmpr': 0b010101,
    'call': 0b010110,
    'ret': 0b010111,
    'beq': 0b011000,
    'bneq': 0b011001,
}

OP_R_R_IMM_INSTRS = ['beq', 'bneq']
OP_R_R_INSTRS = ['movr', 'load', 'str', 'add', 'sub', 'mul', 'and', 'or', 'xor']
OP_R_IMM_INSTRS = ['movi', 'addi', 'subi', 'muli', 'andi', 'ori', 'xori', 'sll', 'srl']
OP_IMM_INSTRS = ['jmp', 'call']
OP_R_INSTRS = ['not', 'jmpr']
OP_INSTRS = ['nop', 'ret']

# Dirty global variables. Stop me.
line_num = 1
label_offsets = {}

def register_string_to_number(r):
    die_if(r not in REGISTERS, 'Invalid register on line {}: {}'.format(line_num, r))
    return int(r[2:])

def resolve_id_or_number(string, max_bin_repr_width):
    if re.match(ID_REGEX, string):
        if string not in label_offsets:
            print("Invalid label on line {}: {}".format(line_num, string))
        return label_offsets[string]

    if '0b' in string:
        number = int(string[2:], 2)
    elif '0x' in string:
        number = int(string[2:], 16)
    else:
        number = int(string, 10)

    rightmost_one = int(math.log2(number)) + 1 if number != 0 else 0
    die_if(rightmost_one > max_bin_repr_width, 'Invalid immediate bit length on line {}: {}'.format(line_num, string))

    return number

def op_r_r_imm_encode(instr, r1, r2, imm):
    op = INSTR_TO_OPCODE[instr]
    r1 = register_string_to_number(r1)
    r2 = register_string_to_number(r2)
    imm = resolve_id_or_number(imm, 16)
    return (op << 26) | (r1 << 21) | (r2 << 16) | imm

def op_r_r_encode(instr, r1, r2):
    op = INSTR_TO_OPCODE[instr]
    r1 = register_string_to_number(r1)
    r2 = register_string_to_number(r2)
    return (op << 26) | (r1 << 21) | (r2 << 16)

def op_r_imm_encode(instr, r, imm):
    op = INSTR_TO_OPCODE[instr]
    r = register_string_to_number(r)
    imm = resolve_id_or_number(imm, 21)
    return (op << 26) | (r << 21) | imm

def op_r_encode(instr, r):
    op = INSTR_TO_OPCODE[instr]
    r = register_string_to_number(r)
    return (op << 26) | (r << 21)

def op_imm_encode(instr, imm):
    op = INSTR_TO_OPCODE[instr]
    imm = resolve_id_or_number(imm, 26)
    return (op << 26) | imm

def op_encode(instr):
    op = INSTR_TO_OPCODE[instr]
    return (op << 26)



die_if(len(sys.argv) == 1, 'Supply a filepath!')
src_path = sys.argv[1]

with open(src_path, 'r') as src_file:
    src = src_file.readlines()

current_offset = 0

# Get labels in the first pass
for line in src:
    code = line.split('#')[0].strip()
    if len(code) == 0:
        continue

    offset_stride = 0
    if ':' in code:
        label = code[:code.find(':')]
        label_offsets[label] = current_offset
        offset_stride = 0
    else:
        offset_stride = 1

    current_offset += offset_stride

encoded_bytes = []

for line in src:
    code = line.split('#')[0].strip()
    if len(code) == 0:
        continue

    offset_stride = 0
    if ':' not in code:
        tokenized = [i.replace(',', '') for i in code.split()]

        instr = tokenized[0]
        if instr in OP_R_R_IMM_INSTRS:
            encoded = op_r_r_imm_encode(instr, tokenized[1], tokenized[2], tokenized[3])
        elif instr in OP_R_R_INSTRS:
            encoded = op_r_r_encode(instr, tokenized[1], tokenized[2])
        elif instr in OP_R_IMM_INSTRS:
            encoded = op_r_imm_encode(instr, tokenized[1], tokenized[2])
        elif instr in OP_R_INSTRS:
            encoded = op_r_encode(instr, tokenized[1])
        elif instr in OP_IMM_INSTRS:
            encoded = op_imm_encode(instr, tokenized[1])
        elif instr in OP_INSTRS:
            encoded = op_encode(instr)
        else:
            die('Invalid instruction on line {}: {}'.format(line_num, instr))

        encoded_bytes.extend([(encoded >> i) & 0xff for i in (24, 16, 8, 0)])

        offset_stride = 4

    current_offset += offset_stride
    line_num += 1

out_path = src_path.replace(".sm", ".mes")
with open(out_path, 'wb') as out_file:
    out_file.write(bytearray(encoded_bytes))