#!/usr/bin/env python3
"""Verify a ready-to-extract archive before installation; never extracts files."""
import argparse
import hashlib
import io
import json
from pathlib import PurePosixPath
import posixpath
import tarfile

ROOT = 'Proton-11.0-ESO-Performance-Hotpatch-arm64'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('archive')
args = parser.parse_args()
actual = {}
expected = None
names = set()
with tarfile.open(args.archive, mode='r|gz') as archive:
    for member in archive:
        name = PurePosixPath(member.name)
        if name.is_absolute() or '..' in name.parts or name.parts[0] != ROOT or member.name in names:
            raise SystemExit('Unsafe or duplicate archive path')
        names.add(member.name)
        relative = name.relative_to(ROOT).as_posix()
        if '__pycache__' in name.parts or any(p.startswith('default_pfx') for p in name.parts):
            raise SystemExit('Generated prefix/cache in archive')
        if member.uid or member.gid or member.uname or member.gname:
            raise SystemExit('Noncanonical owner metadata')
        if member.issym():
            target = posixpath.normpath(posixpath.join(str(name.parent), member.linkname))
            if member.linkname.startswith('/') or not target.startswith(ROOT+'/'):
                raise SystemExit('External archive symlink')
        elif member.isfile():
            source = archive.extractfile(member)
            if relative == 'eso-hotpatch/RUNTIME-SHA256SUMS':
                expected = dict((name, value) for value,name in (line.split('  ',1) for line in source.read().decode().splitlines()))
            else:
                digest = hashlib.sha256()
                if relative == 'steampipe_fixups.json':
                    payload = source.read()
                    fixups = json.loads(payload)
                    if any(name.startswith('files/share/default_pfx') for key in ['empty_dirs','no_write_paths'] for name in fixups[key]):
                        raise SystemExit('Omitted prefix would be recreated by SteamPipe fixups')
                    source = io.BytesIO(payload)
                for block in iter(lambda: source.read(1024*1024), b''):
                    digest.update(block)
                actual[relative] = digest.hexdigest()
        elif not member.isdir():
            raise SystemExit('Unsupported special archive member')
if actual != expected:
    raise SystemExit('Runtime file checksums differ from the internal manifest')
for name, expected_hash in [('kernel32.dll','dbf5fa3a80204259f8e42e9a4ebcbdd6769f3f86301aa9da39f22797e0e40257'),('ntdll.dll','74e45da0005fa0c890bdb3cc78e14af1d590fc8e22bc51a633755e0f47426eb2')]:
    if actual['files/lib/wine/aarch64-windows/'+name] != expected_hash:
        raise SystemExit('Unexpected patched DLL')
print('PASS: ready runtime,',len(actual),'file hashes, safe paths/links, canonical owners, no generated prefix')
