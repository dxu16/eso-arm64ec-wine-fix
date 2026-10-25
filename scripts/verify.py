#!/usr/bin/env python3
"""Verify the manifest, exact DLL reproduction, rejection guards and optional release assets."""
import argparse
import ast
import hashlib
import io
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import tarfile

ROOT = Path(__file__).resolve().parents[1]
BASE = '472d5a6b9906e90262dfacb5ed7ced11c76e8dbdd95037e424cf4fd7412299c6'
PATCHED = 'dbf5fa3a80204259f8e42e9a4ebcbdd6769f3f86301aa9da39f22797e0e40257'


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
    measured = json.loads((ROOT/'evidence/validation-results.json').read_text())['input_component_hashes']
    installer = ast.parse((ROOT/'scripts/install.py').read_text())
    for statement in installer.body:
        if isinstance(statement, ast.Assign) and any(isinstance(t, ast.Name) and t.id in {'BASE_HASHES', 'BASE_UNIX_HASHES'} for t in statement.targets):
            for name, value in ast.literal_eval(statement.value).items():
                check(len(value) == 64 and all(c in '0123456789abcdef' for c in value), 'Malformed installer hash: '+name)
                check(value == measured[name], 'Installer hash differs from measured baseline: '+name)
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
    nt_manifest = json.loads((ROOT/'patches/ntdll-performance.json').read_text())
    nt_patched = (ROOT/'bin/ntdll-eso-performance.dll').read_bytes()
    check(hashlib.sha256(nt_patched).hexdigest() == nt_manifest['output_sha256'], 'ntdll checksum failed')
    nt_original = bytearray(nt_patched)
    for row in nt_manifest['changes']:
        pos = int(row['file_offset'], 16)
        old, new = bytes.fromhex(row['old']), bytes.fromhex(row['new'])
        check(len(old) == len(new) and nt_original[pos:pos+len(new)] == new, 'ntdll manifest mismatch')
        nt_original[pos:pos+len(old)] = old
    check(hashlib.sha256(nt_original).hexdigest() == nt_manifest['input_sha256'], 'ntdll baseline reconstruction failed')
    helper = struct.unpack_from('<8I', nt_patched, int(nt_manifest['helper_rva'], 16))
    check(helper == (0x58000111, 0xeb11021f, 0x54000080, 0x58ec56b1, 0x17ff628b, 0xd503201f, 0x9100216b, 0x17ff62a4), 'Native helper differs from independently assembled reference')
    with tempfile.TemporaryDirectory(prefix='eso-hotpatch-verify-', dir=ROOT) as temporary:
        d = Path(temporary)
        source, destination, unknown = d/'ntdll-original.dll', d/'ntdll-output.dll', d/'unknown.dll'
        source.write_bytes(nt_original)
        unknown.write_bytes(b'unsupported input')
        script = str(ROOT/'scripts/reproduce-ntdll-performance.py')
        subprocess.run([sys.executable, '-B', script, str(source), str(destination)], check=True)
        check(destination.read_bytes() == nt_patched, 'ntdll CLI reproduction failed')
        for src, dst in [(source,source), (source,destination), (unknown,d/'rejected.dll')]:
            result = subprocess.run([sys.executable, '-B', '-O', script, str(src), str(dst)], capture_output=True)
            check(result.returncode != 0, 'ntdll guard accepted unsafe input/output')
        check(not (d/'rejected.dll').exists(), 'Rejected ntdll input created output')
    with tempfile.TemporaryDirectory(prefix='eso-hotpatch-verify-', dir=ROOT) as temporary:
        d = Path(temporary)
        verifier = str(ROOT/'scripts/verify-runtime.py')
        tool_id = 'Proton-11.0-ESO-Performance-Hotpatch-arm64'
        valid = d/'valid-runtime.tar.gz'
        entries = {'files/lib/wine/aarch64-windows/kernel32.dll': patched,
                   'files/lib/wine/aarch64-windows/ntdll.dll': nt_patched,
                   'steampipe_fixups.json': b'{"empty_dirs":[],"no_write_paths":[]}'}
        with tarfile.open(valid, 'w:gz') as archive:
            for name, payload in entries.items():
                member = tarfile.TarInfo(tool_id+'/'+name)
                member.size = len(payload)
                archive.addfile(member, io.BytesIO(payload))
            sums = ''.join(hashlib.sha256(value).hexdigest()+'  '+name+'\n' for name,value in entries.items()).encode()
            member = tarfile.TarInfo(tool_id+'/eso-hotpatch/RUNTIME-SHA256SUMS')
            member.size = len(sums)
            archive.addfile(member, io.BytesIO(sums))
        subprocess.run([sys.executable, '-B', verifier, str(valid)], check=True)
        for kind, message in [('traversal','Unsafe'),('symlink','External'),('prefix','Generated'),('owner','Noncanonical')]:
            path = d/(kind+'.tar.gz')
            member = tarfile.TarInfo('../escape' if kind=='traversal' else tool_id+'/entry')
            if kind=='symlink':
                member.type, member.linkname = tarfile.SYMTYPE, '../../../outside'
            if kind=='prefix':
                member.name = tool_id+'/files/share/default_pfx_arm64/system.reg'
            if kind=='owner':
                member.uid = 12345
            with tarfile.open(path, 'w:gz') as archive:
                archive.addfile(member)
            result = subprocess.run([sys.executable, '-B', verifier, str(path)], capture_output=True, text=True)
            check(result.returncode != 0 and message in result.stderr, 'Runtime archive guard failed: '+kind)
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
    print('PASS: both DLLs, 796 preserved import targets, native helper, exact reproduction, and rejection guards')


if __name__ == '__main__':
    main()
