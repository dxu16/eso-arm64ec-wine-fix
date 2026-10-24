#!/usr/bin/env python3
"""Verify the manifest, exact DLL reproduction, rejection guards and optional release assets."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BASE = 'fed36267d61204658b96a976e4cf19ab1053c49a466ca58c2bde6089148773cb'
PATCHED = '5b9c2d116f93a307e7b69c31544e52b7a5081fa7caa384020b1c09f948664d5b'


def check(value, message):
    if not value:
        raise SystemExit(message)


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--release-assets', action='store_true')
    args = parser.parse_args()
    patched = (ROOT / 'bin/kernel32-eso-hotpatch.dll').read_bytes()
    check(hashlib.sha256(patched).hexdigest() == PATCHED, 'Compiled DLL checksum failed')
    manifest = json.loads((ROOT / 'patches/kernel32-hotpatch-thunks.json').read_text())
    check(len(manifest['changes']) == 796, 'Unexpected manifest count')
    pe = struct.unpack_from('<I', patched, 0x3c)[0]
    n = struct.unpack_from('<H', patched, pe+6)[0]
    opt = struct.unpack_from('<H', patched, pe+20)[0]
    sections = [struct.unpack_from('<IIII', patched, pe+24+opt+40*i+8) for i in range(n)]
    original = bytearray(patched)
    for row in manifest['changes']:
        rva = int(row['rva'], 16)
        candidates = [ptr+rva-va for size,va,raw,ptr in sections if va <= rva and rva+16 <= va+raw]
        check(len(candidates) == 1, 'Invalid manifest RVA')
        pos = candidates[0]
        old, new = bytes.fromhex(row['old']), bytes.fromhex(row['new'])
        check(original[pos:pos+16] == new, 'Manifest replacement mismatch')
        check(rva+6+struct.unpack_from('<i',old,2)[0] == rva+14+struct.unpack_from('<i',new,10)[0], 'Import target changed')
        original[pos:pos+16] = old
    check(hashlib.sha256(original).hexdigest() == BASE, 'Reconstructed baseline mismatch')
    with tempfile.TemporaryDirectory(prefix='eso-hotpatch-verify-', dir=ROOT) as temporary:
        d = Path(temporary)
        baseline, output, bad = d/'baseline.dll', d/'output.dll', d/'unknown.dll'
        baseline.write_bytes(original)
        bad.write_bytes(b'not a supported DLL')
        script = str(ROOT/'scripts/reproduce-kernel32-hotpatch.py')
        subprocess.run([sys.executable, '-B', script, str(baseline), str(output)], check=True)
        check(output.read_bytes() == patched, 'CLI reproduction differs')
        cases = [(baseline,baseline), (baseline,output), (bad,d/'rejected.dll')]
        for source,destination in cases:
            result = subprocess.run([sys.executable, '-B', '-O', script, str(source), str(destination)], capture_output=True)
            check(result.returncode != 0, 'Unsafe input/output was accepted')
        check(not (d/'rejected.dll').exists(), 'Rejected input created an output')
    if (ROOT/'SHA256SUMS').exists():
        for line in (ROOT/'SHA256SUMS').read_text().splitlines():
            expected, name = line.split('  ',1)
            check(digest(ROOT/name) == expected, 'Repository checksum failed: '+name)
    if args.release_assets:
        for row in json.loads((ROOT/'release-manifest.json').read_text())['assets']:
            path = ROOT/'release-assets'/row['name']
            check(path.is_file(), 'Missing release asset: '+str(path))
            check(digest(path) == row['sha256'], 'Release checksum failed: '+row['name'])
            print('Verified release asset:', row['name'])
    print('PASS: DLL, 796 preserved import targets, exact reproduction, and rejection guards')


if __name__ == '__main__':
    main()
