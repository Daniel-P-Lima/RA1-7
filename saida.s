.arch_extension idiv   @ habilita SDIV em ARM mode (Cortex-A9)
.global _start

_start:
    LDR sp, =0x3FFFFFFC    @ inicializar pilha (fim da SDRAM)
    @ --- Linha 1 ---
    LDR r0, =_c1_0
    VLDR d0, [r0]
    LDR r0, =_c1_1
    VLDR d1, [r0]
    VADD.F64 d0, d0, d1
    LDR r0, =_result_1
    VSTR d0, [r0]
    VCVT.S32.F64 s0, d0    @ truncar resultado para inteiro
    VMOV r1, s0
    BL _show_hex

    @ --- Linha 2 ---
    LDR r0, =_c2_0
    VLDR d0, [r0]
    LDR r0, =_c2_1
    VLDR d1, [r0]
    VCVT.S32.F64 s0, d0
    VCVT.S32.F64 s2, d1
    VMOV r0, s0
    VMOV r1, s2
    SDIV r0, r0, r1
    VMOV s0, r0
    VCVT.F64.S32 d0, s0
    @ ERRO: operador '/' sem operandos suficientes (linha 2)

    @ --- Linha 3 ---
    LDR r0, =_c3_0
    VLDR d0, [r0]
    LDR r0, =_c3_1
    VLDR d1, [r0]
    VADD.F64 d0, d0, d1
    LDR r0, =_c3_2
    VLDR d1, [r0]
    VMUL.F64 d0, d0, d1
    LDR r0, =_result_3
    VSTR d0, [r0]
    VCVT.S32.F64 s0, d0    @ truncar resultado para inteiro
    VMOV r1, s0
    BL _show_hex

    @ --- Linha 4 ---
    LDR r0, =_c4_0
    VLDR d0, [r0]
    LDR r0, =_c4_1
    VLDR d1, [r0]
    LDR r0, =_c4_2
    VLDR d2, [r0]
    VADD.F64 d1, d1, d2
    LDR r0, =_c4_3
    VLDR d2, [r0]
    VMUL.F64 d1, d1, d2
    VADD.F64 d0, d0, d1
    LDR r0, =_c4_4
    VLDR d1, [r0]
    VSUB.F64 d0, d0, d1
    LDR r0, =_result_4
    VSTR d0, [r0]
    VCVT.S32.F64 s0, d0    @ truncar resultado para inteiro
    VMOV r1, s0
    BL _show_hex

    @ --- Linha 5 ---
    LDR r0, =_c5_0
    VLDR d0, [r0]
    LDR r0, =_c5_1
    VLDR d1, [r0]
    LDR r0, =_c5_2
    VLDR d2, [r0]
    VMUL.F64 d1, d1, d2
    VSUB.F64 d0, d0, d1
    LDR r0, =_result_5
    VSTR d0, [r0]
    VCVT.S32.F64 s0, d0    @ truncar resultado para inteiro
    VMOV r1, s0
    BL _show_hex

    @ --- Linha 6 ---
    LDR r0, =_c6_0
    VLDR d0, [r0]
    LDR r0, =_c6_1
    VLDR d1, [r0]
    VADD.F64 d0, d0, d1
    LDR r0, =_c6_2
    VLDR d1, [r0]
    VMUL.F64 d0, d0, d1
    LDR r0, =_result_6
    VSTR d0, [r0]
    VCVT.S32.F64 s0, d0    @ truncar resultado para inteiro
    VMOV r1, s0
    BL _show_hex

    @ --- Linha 7 ---
    LDR r0, =_c7_0
    VLDR d0, [r0]
    LDR r0, =_c7_1
    VLDR d1, [r0]
    VCVT.S32.F64 s0, d0
    VCVT.S32.F64 s2, d1
    VMOV r0, s0
    VMOV r1, s2
    SDIV r0, r0, r1
    VMOV s0, r0
    VCVT.F64.S32 d0, s0
    LDR r0, =_result_7
    VSTR d0, [r0]
    VCVT.S32.F64 s0, d0    @ truncar resultado para inteiro
    VMOV r1, s0
    BL _show_hex

    @ --- Linha 8 ---
    LDR r0, =_c8_0
    VLDR d0, [r0]
    LDR r0, =_c8_1
    VLDR d1, [r0]
    VCVT.S32.F64 s0, d0
    VCVT.S32.F64 s2, d1
    VMOV r0, s0
    VMOV r1, s2
    SDIV r2, r0, r1
    MUL r2, r2, r1
    SUB r0, r0, r2
    VMOV s0, r0
    VCVT.F64.S32 d0, s0
    LDR r0, =_result_8
    VSTR d0, [r0]
    VCVT.S32.F64 s0, d0    @ truncar resultado para inteiro
    VMOV r1, s0
    BL _show_hex

    @ --- Linha 9 ---
    LDR r0, =_c9_0
    VLDR d0, [r0]
    LDR r0, =_c9_1
    VLDR d1, [r0]
    @ Potenciacao: d0 ^ d1
    VCVT.S32.F64 s4, d1
    VMOV r2, s4
    LDR r0, =_c9_2
    VLDR d1, [r0]
_pow_loop_9_0:
    CMP r2, #0
    BEQ _pow_done_9_0
    VMUL.F64 d1, d1, d0
    SUB r2, r2, #1
    B _pow_loop_9_0
_pow_done_9_0:
    VMOV.F64 d0, d1
    LDR r0, =_result_9
    VSTR d0, [r0]
    VCVT.S32.F64 s0, d0    @ truncar resultado para inteiro
    VMOV r1, s0
    BL _show_hex

    @ --- Linha 10 ---
    LDR r0, =_c10_0
    VLDR d0, [r0]
    LDR r0, =_c10_1
    VLDR d1, [r0]
    LDR r0, =_c10_2
    VLDR d2, [r0]
    VMUL.F64 d1, d1, d2
    VADD.F64 d0, d0, d1
    LDR r0, =_result_10
    VSTR d0, [r0]
    VCVT.S32.F64 s0, d0    @ truncar resultado para inteiro
    VMOV r1, s0
    BL _show_hex

    @ --- Linha 11 ---
    LDR r0, =_c11_0
    VLDR d0, [r0]
    LDR r0, =_c11_1
    VLDR d1, [r0]
    VMUL.F64 d0, d0, d1
    LDR r0, =_c11_2
    VLDR d1, [r0]
    VMUL.F64 d0, d0, d1
    LDR r0, =_c11_3
    VLDR d1, [r0]
    VDIV.F64 d0, d0, d1
    LDR r0, =_result_11
    VSTR d0, [r0]
    VCVT.S32.F64 s0, d0    @ truncar resultado para inteiro
    VMOV r1, s0
    BL _show_hex

    @ --- Linha 12 ---
    LDR r0, =_c12_0
    VLDR d0, [r0]
    @ RES 4: resultado da linha 8
    LDR r0, =_result_8
    VLDR d0, [r0]
    LDR r0, =_result_12
    VSTR d0, [r0]
    VCVT.S32.F64 s0, d0    @ truncar resultado para inteiro
    VMOV r1, s0
    BL _show_hex

    @ --- Linha 13 ---
    LDR r0, =_c13_0
    VLDR d0, [r0]
    @ Salvar em MEM
    LDR r0, =_mem_MEM
    VSTR d0, [r0]
    LDR r0, =_result_13
    VSTR d0, [r0]
    VCVT.S32.F64 s0, d0    @ truncar resultado para inteiro
    VMOV r1, s0
    BL _show_hex

    @ --- Linha 14 ---
    @ Carregar MEM
    LDR r0, =_mem_MEM
    VLDR d0, [r0]
    LDR r0, =_result_14
    VSTR d0, [r0]
    VCVT.S32.F64 s0, d0    @ truncar resultado para inteiro
    VMOV r1, s0
    BL _show_hex

_halt:
    B _halt

@ Subrotina: exibe inteiro com sinal em HEX0-3 e LEDR
@ Entrada: r1 = valor inteiro com sinal (parte inteira do resultado)
@ HEX mostra parte inteira; LEDR mostra bits brutos
_show_hex:
    PUSH {r2, r3, r4, r5, r6, lr}
    LDR r0, =0xFF200000        @ LEDR
    STR r1, [r0]
    LDR r0, =0xFF200030        @ HEX4-5
    CMP r1, #0
    BPL _show_hex_pos
    MOV r2, #0x40              @ sinal de menos no HEX5
    LSL r2, r2, #8
    STR r2, [r0]
    NEG r1, r1
    B _show_hex_digits
_show_hex_pos:
    MOV r2, #0
    STR r2, [r0]               @ apaga HEX4-5
_show_hex_digits:
    LDR r5, =_seg7_table
    MOV r6, #0                 @ palavra acumuladora dos segmentos
    MOV r2, #10
    @ HEX0: digito das unidades
    SDIV r3, r1, r2
    MUL r4, r3, r2
    SUB r4, r1, r4
    LDRB r4, [r5, r4]
    ORR r6, r6, r4
    MOV r1, r3
    @ HEX1: digito das dezenas
    SDIV r3, r1, r2
    MUL r4, r3, r2
    SUB r4, r1, r4
    LDRB r4, [r5, r4]
    LSL r4, r4, #8
    ORR r6, r6, r4
    MOV r1, r3
    @ HEX2: digito das centenas
    SDIV r3, r1, r2
    MUL r4, r3, r2
    SUB r4, r1, r4
    LDRB r4, [r5, r4]
    LSL r4, r4, #16
    ORR r6, r6, r4
    MOV r1, r3
    @ HEX3: digito das centenas
    SDIV r3, r1, r2
    MUL r4, r3, r2
    SUB r4, r1, r4
    LDRB r4, [r5, r4]
    LSL r4, r4, #24
    ORR r6, r6, r4
    @ Supressao de zeros a esquerda
    @ Se HEX3 == segmento '0' (0x3F), apaga
    LSR r3, r6, #24
    CMP r3, #0x3F
    BNE _no_blank_hex3
    BIC r6, r6, #0xFF000000
_no_blank_hex3:
    @ Se HEX3 apagado E HEX2 == '0', apaga HEX2 tambem
    TST r6, #0xFF000000
    BNE _no_blank_hex2
    LSR r3, r6, #16
    AND r3, r3, #0xFF
    CMP r3, #0x3F
    BNE _no_blank_hex2
    BIC r6, r6, #0x00FF0000
_no_blank_hex2:
    LDR r0, =0xFF200020        @ HEX0-3
    STR r6, [r0]
    POP {r2, r3, r4, r5, r6, pc}

.data
_seg7_table:
    .byte 0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07, 0x7F, 0x6F
.align 8
_c1_0: .double 3
.align 8
_c1_1: .double 4
.align 8
_result_1: .space 8
.align 8
_c2_0: .double 10
.align 8
_c2_1: .double 2
.align 8
_result_2: .space 8
.align 8
_c3_0: .double 3.1400000000000001
.align 8
_c3_1: .double 2
.align 8
_c3_2: .double 9
.align 8
_result_3: .space 8
.align 8
_c4_0: .double 5
.align 8
_c4_1: .double 1
.align 8
_c4_2: .double 2
.align 8
_c4_3: .double 4
.align 8
_c4_4: .double 3
.align 8
_result_4: .space 8
.align 8
_c5_0: .double 7
.align 8
_c5_1: .double 2
.align 8
_c5_2: .double 3
.align 8
_result_5: .space 8
.align 8
_c6_0: .double 8
.align 8
_c6_1: .double 3
.align 8
_c6_2: .double 2
.align 8
_result_6: .space 8
.align 8
_c7_0: .double 8
.align 8
_c7_1: .double 2
.align 8
_result_7: .space 8
.align 8
_c8_0: .double 42
.align 8
_c8_1: .double 7
.align 8
_result_8: .space 8
.align 8
_c9_0: .double 2
.align 8
_c9_1: .double 3
.align 8
_c9_2: .double 1
.align 8
_result_9: .space 8
.align 8
_c10_0: .double 1
.align 8
_c10_1: .double 2
.align 8
_c10_2: .double 3
.align 8
_result_10: .space 8
.align 8
_c11_0: .double 5
.align 8
_c11_1: .double 2
.align 8
_c11_2: .double 190
.align 8
_c11_3: .double 4
.align 8
_result_11: .space 8
.align 8
_c12_0: .double 4
.align 8
_result_12: .space 8
.align 8
_c13_0: .double 123
.align 8
_mem_MEM: .double 0.0
.align 8
_result_13: .space 8
.align 8
_result_14: .space 8