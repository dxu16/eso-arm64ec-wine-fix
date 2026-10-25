.text
.org 0xc9278
    b candidate_helper
original_compare:
    nop
.org 0xc92ec
jump_check:
    nop
.org 0xc9320
fastforward_literal:
    .byte 0x48,0x8b,0xc4,0x48,0x89,0x58,0x20,0x55,0x5d,0xe9
.org 0xf0840
candidate_helper:
    ldr x17, identity_lea
    cmp x16, x17
    b.eq skip_identity
    ldr x17, fastforward_literal
    b original_compare
    nop
skip_identity:
    add x11, x11, #8
    b jump_check
identity_lea:
    .byte 0x48,0x8d,0xa4,0x24,0,0,0,0
