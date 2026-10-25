"""Reproduce the exact Valve Wine ARM64EC call-checker performance correction.

Only writes a separate output DLL. This is not a FEX source change.
"""
from pathlib import Path
import hashlib
import json
import struct
import argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('source', type=Path)
parser.add_argument('output', type=Path)
args = parser.parse_args()
source, output = args.source, args.output
original = source.read_bytes()
if not (hashlib.sha256(original).hexdigest() == '5bab1f413ea1032ba9d1fd8a500b83d0248092e1911ba487a96d797fe062b71f'):
    raise SystemExit('Unsupported input/layout or unsafe output; no DLL written')
if not (source.resolve() != output.resolve() and not output.exists()):
    raise SystemExit('Unsupported input/layout or unsafe output; no DLL written')
data = bytearray(original)
pe = struct.unpack_from('<I', data, 60)[0]
optional_size = struct.unpack_from('<H', data, pe + 20)[0]
section = pe + 24 + optional_size
if not (data[section:section + 8].rstrip(b'\0') == b'.text'):
    raise SystemExit('Unsupported input/layout or unsafe output; no DLL written')
virtual_size, virtual_address, raw_size, raw_pointer = struct.unpack_from('<IIII', data, section + 8)
if not (virtual_address == raw_pointer == 0x10000):
    raise SystemExit('Unsupported input/layout or unsafe output; no DLL written')
call = 0xc9274
site = call + 4
resume = call + 8
jump_check = 0xc92ec
if not (data[call:call + 16] == bytes.fromhex('700140f9510500581f0211eb41010054')):
    raise SystemExit('Unsupported input/layout or unsafe output; no DLL written')
if not (data[jump_check:jump_check + 8] == bytes.fromhex('700140391ffe0371')):
    raise SystemExit('Unsupported input/layout or unsafe output; no DLL written')
instruction = struct.unpack_from('<I', data, site)[0]
immediate = (instruction >> 5) & 0x7ffff
if immediate & 0x40000:
    immediate -= 0x80000
old_literal = site + immediate * 4
if not (data[old_literal:old_literal + 10] == bytes.fromhex('488bc448895820555de9')):
    raise SystemExit('Unsupported input/layout or unsafe output; no DLL written')
image_base = struct.unpack_from('<Q', data, pe + 24 + 24)[0]
load_config = struct.unpack_from('<I', data, pe + 24 + 112 + 80)[0]
metadata = struct.unpack_from('<Q', data, load_config + 200)[0] - image_base
code_map, code_count = struct.unpack_from('<II', data, metadata + 4)
if not (code_count == 3):
    raise SystemExit('Unsupported input/layout or unsafe output; no DLL written')
ec_map_entry = code_map + 8
ec_start, ec_size = struct.unpack_from('<II', data, ec_map_entry)
if not (ec_start == 0x83001 and ec_size == 0x6d840):
    raise SystemExit('Unsupported input/layout or unsafe output; no DLL written')
ec_base = ec_start & ~3
cave = (ec_base + ec_size + 15) & ~15
if not (cave == 0xf0840 and cave + 40 <= virtual_address + virtual_size):
    raise SystemExit('Unsupported input/layout or unsafe output; no DLL written')
if not (data[cave:cave + 40] == bytes(40)):
    raise SystemExit('Unsupported input/layout or unsafe output; no DLL written')

def branch(pc, target):
    delta = target - pc
    if not (delta % 4 == 0 and -(1 << 27) <= delta < 1 << 27):
        raise SystemExit('Unsupported input/layout or unsafe output; no DLL written')
    return 0x14000000 | ((delta // 4) & 0x3ffffff)

def conditional_equal(pc, target):
    delta = target - pc
    if not (delta % 4 == 0 and -(1 << 20) <= delta < 1 << 20):
        raise SystemExit('Unsupported input/layout or unsafe output; no DLL written')
    return 0x54000000 | (((delta // 4) & 0x7ffff) << 5)

def load_literal_x17(pc, target):
    delta = target - pc
    if not (delta % 4 == 0 and -(1 << 20) <= delta < 1 << 20):
        raise SystemExit('Unsupported input/layout or unsafe output; no DLL written')
    return 0x58000011 | (((delta // 4) & 0x7ffff) << 5)

instructions = [
    load_literal_x17(cave, cave + 32),
    0xeb11021f,  # cmp x16, x17
    conditional_equal(cave + 8, cave + 24),
    load_literal_x17(cave + 12, old_literal),
    branch(cave + 16, resume),
    0xd503201f,  # nop
    0x9100216b,  # add x11, x11, #8
    branch(cave + 28, jump_check),
]
data[cave:cave + 40] = struct.pack('<8I', *instructions) + bytes.fromhex('488da42400000000')
struct.pack_into('<I', data, site, branch(site, cave))
struct.pack_into('<I', data, ec_map_entry + 4, cave + 40 - ec_base)
if not (len(data) == len(original)):
    raise SystemExit('Unsupported input/layout or unsafe output; no DLL written')
if hashlib.sha256(data).hexdigest() != '74e45da0005fa0c890bdb3cc78e14af1d590fc8e22bc51a633755e0f47426eb2':
    raise SystemExit('Output checksum failed; no DLL written')
with output.open('xb') as stream:
    stream.write(data)
print(json.dumps({'input_sha256': hashlib.sha256(original).hexdigest(),
                  'output_sha256': hashlib.sha256(data).hexdigest(),
                  'call_checker_site': hex(site), 'helper_rva': hex(cave),
                  'original_fast_forward_literal': hex(old_literal),
                  'changed_byte_count': sum(a != b for a, b in zip(original, data)),
                  'helper_instructions': [hex(x) for x in instructions]}, indent=2))
