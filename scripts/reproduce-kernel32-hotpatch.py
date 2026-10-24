#!/usr/bin/env python3
"""Reproduce the private BNet1 imported-export hotpatch-prolog experiment.

Reads the original DLL and writes a separate output. Never modifies ESO or input.
Requires the adjacent recorded manifest; refuses unknown runtime versions.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

BASE_SHA = 'fed36267d61204658b96a976e4cf19ab1053c49a466ca58c2bde6089148773cb'
OUT_SHA = '5b9c2d116f93a307e7b69c31544e52b7a5081fa7caa384020b1c09f948664d5b'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('input', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
if not (args.input.resolve() != args.output.resolve()): raise SystemExit('Separate output required')
if not (not args.output.exists()): raise SystemExit('Output already exists')
b = bytearray(args.input.read_bytes())
if not (hashlib.sha256(b).hexdigest() == BASE_SHA): raise SystemExit('Unknown baseline DLL')
pe = struct.unpack_from('<I', b, 0x3c)[0]
n = struct.unpack_from('<H', b, pe + 6)[0]
opt = struct.unpack_from('<H', b, pe + 20)[0]
sections = [struct.unpack_from('<IIII', b, pe + 24 + opt + 40*i + 8) for i in range(n)]
def offset(rva):
    for size, va, raw, ptr in sections:
        if va <= rva < va + raw:
            return ptr + rva - va
    raise ValueError(hex(rva))
manifest = json.loads((Path(__file__).resolve().parents[1] / 'patches/kernel32-hotpatch-thunks.json').read_text())
if not (len(manifest['changes']) == 796): raise SystemExit('Patch validation failed')
for row in manifest['changes']:
    rva = int(row['rva'], 16)
    pos = offset(rva)
    old, new = bytes.fromhex(row['old']), bytes.fromhex(row['new'])
    if not (bytes(b[pos:pos + 16]) == old): raise SystemExit('Patch validation failed')
    if not (old[:2] == bytes.fromhex('ff25') and set(old[6:]) <= {0, 204}): raise SystemExit('Patch validation failed')
    if not (new[:10] == bytes.fromhex('488da42400000000ff25')): raise SystemExit('Patch validation failed')
    # Both instructions address exactly the same original import slot.
    if not (rva + 6 + struct.unpack_from('<i', old, 2)[0] == rva + 14 + struct.unpack_from('<i', new, 10)[0]): raise SystemExit('Patch validation failed')
    b[pos:pos+16] = new
if not (hashlib.sha256(b).hexdigest() == OUT_SHA): raise SystemExit('Patch validation failed')
with args.output.open('xb') as output:
    output.write(b)
print('Wrote', args.output, 'with 796 x64 Wine hotpatch entry prologs; SHA256', OUT_SHA)
