.text
.org 825624
b helper
resume:
.org 825740
jump_check:
nop
.org 825792
old_literal:
.quad 0
.org 987664
helper:
ldr x17, prolog
cmp x16, x17
b.eq matched
ldr x17, old_literal
b resume
nop
matched:
add x11, x11, #8
b jump_check
prolog:
.byte 0x48,0x8d,0xa4,0x24,0,0,0,0
