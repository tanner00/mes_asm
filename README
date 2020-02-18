## Definition of the MES ISA

### Design decisions:

Word size: 32 bits

32 registers ($r0 hardwired to 0)

Fixed width instructions which match the word size

Word addressable memory (for now)

64 potential opcodes (26 used right now)

#### MimasV2-enforced specs

100 MHz

64 MB of memory (16 MegaWords)

2 MB ROM

### Instructions

nop (nop)

movi (movi $r, imm)

movr (movr $r1, $r2)

load (load $r1, $r2)

str (str $r1, $r2)

add (add $r1, $r2)

addi (addi $r, imm)

sub (sub $r1, $r2)

subi (subi $r, imm)

mul (mul $r1, $r2)

muli (mul $r, imm)

and (and $r1, $r2)

andi (andi $r, imm)

or (or $r1, $r2)

ori (ori $r, imm)

xor (xor $r1, $r2)

xori (xor $r, imm)

not (not $r)

sll (sll $r, imm)

srl (srl $r, imm)

jmp (jmp imm)

jmpr (jmpr $r)

call (call imm)

ret (ret)

beq (beq $r1, $r2, imm)

bneq (bneq $r1, $r2, imm)
