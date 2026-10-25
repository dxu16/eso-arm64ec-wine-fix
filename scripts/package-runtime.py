#!/usr/bin/env python3
"""Package a prepared official-base tool without prefixes, caches, or device data."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import stat
import tarfile

TOOL_ID = 'Proton-11.0-ESO-Performance-Hotpatch-arm64'
PATCHED = {
    'kernel32.dll': 'dbf5fa3a80204259f8e42e9a4ebcbdd6769f3f86301aa9da39f22797e0e40257',
    'ntdll.dll': '74e45da0005fa0c890bdb3cc78e14af1d590fc8e22bc51a633755e0f47426eb2',
}
SECRET = re.compile(rb'-----BEGIN (?:OPENSSH |RSA |DSA |EC |ENCRYPTED )?PRIVATE KEY-----|github_pat_[A-Za-z0-9_]{30,}|gh[pousr]_[A-Za-z0-9]{30,}')


def excluded(relative):
    parts = relative.parts
    return ('__pycache__' in parts or '.git' in parts or
            relative.suffix.lower() in {'.pyc', '.pyo', '.log', '.reg', '.dmp'} or
            relative.as_posix() in {'dist.lock', 'user_settings.py', 'files/steampipe_fixups_mtime'} or
            len(parts) >= 3 and parts[:2] == ('files', 'share') and parts[2].startswith('default_pfx'))


def checked_digest(path, private_patterns):
    digest = hashlib.sha256()
    carry = b''
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024*1024), b''):
            digest.update(block)
            window = carry + block
            if SECRET.search(window) or any(value in window for value in private_patterns):
                raise SystemExit('Credential or device-home data in ' + path.name)
            carry = window[-512:]
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tool', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    tool = args.tool.resolve()
    if args.tool.is_symlink() or not tool.is_dir() or args.output.exists():
        parser.error('Use a real prepared tool directory and a new output filename')
    if args.output.resolve().is_relative_to(tool):
        parser.error('Output must be outside the tool')
    if (tool/'version').read_text().strip() != '1791559733 proton-11.0-2e-arm64':
        parser.error('Unsupported base runtime')
    for name, expected in PATCHED.items():
        if hashlib.sha256((tool/'files/lib/wine/aarch64-windows'/name).read_bytes()).hexdigest() != expected:
            parser.error('Unexpected patched DLL: '+name)
    if not (tool/'eso-hotpatch/LICENSES/runtime/source-index.json').is_file():
        parser.error('Runtime component notices and their source index are required')
    if not (tool/'RUNTIME-SOURCES.txt').is_file():
        parser.error('Matching runtime source archive information is required')
    private = [str(Path.home()).encode(), str(Path.home()).encode('utf-16le')]
    fixups = json.loads((tool/'steampipe_fixups.json').read_text())
    for key in ['empty_dirs', 'no_write_paths']:
        fixups[key] = [name for name in fixups[key] if not name.startswith('files/share/default_pfx')]
    overrides = {'steampipe_fixups.json': (json.dumps(fixups, indent=2)+'\n').encode()}
    members = []
    checksums = []
    for path in sorted(tool.rglob('*')):
        relative = path.relative_to(tool)
        if excluded(relative):
            continue
        if path.name in {'authorized_keys', 'id_ed25519', 'id_rsa', 'loginusers.vdf', '.env'}:
            raise SystemExit('Private filename in runtime: '+relative.as_posix())
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode):
            target = path.readlink()
            if target.is_absolute() or not (path.parent/target).resolve().is_relative_to(tool):
                raise SystemExit('External symlink in runtime: '+relative.as_posix())
        elif stat.S_ISREG(mode):
            digest = checked_digest(path, private)
            if relative.as_posix() in overrides:
                digest = hashlib.sha256(overrides[relative.as_posix()]).hexdigest()
            checksums.append(digest+'  '+relative.as_posix()+'\n')
        elif not stat.S_ISDIR(mode):
            raise SystemExit('Special filesystem node in runtime: '+relative.as_posix())
        members.append((path,relative,mode))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('xb') as raw, gzip.GzipFile(filename='', fileobj=raw, mode='wb', compresslevel=6, mtime=0) as compressed:
        with tarfile.open(fileobj=compressed, mode='w|') as archive:
            for path, relative, mode in members:
                member = tarfile.TarInfo(TOOL_ID+'/'+relative.as_posix())
                member.uid = member.gid = member.mtime = 0
                member.uname = member.gname = ''
                if stat.S_ISLNK(mode):
                    member.type, member.mode = tarfile.SYMTYPE, 0o777
                    member.linkname = str(path.readlink())
                    archive.addfile(member)
                elif stat.S_ISDIR(mode):
                    member.type, member.mode = tarfile.DIRTYPE, 0o755
                    archive.addfile(member)
                else:
                    member.mode = 0o755 if mode & 0o111 else 0o644
                    if relative.as_posix() in overrides:
                        payload = overrides[relative.as_posix()]
                        member.size = len(payload)
                        archive.addfile(member, io.BytesIO(payload))
                    else:
                        member.size = path.stat().st_size
                        with path.open('rb') as source:
                            archive.addfile(member, source)
            data = ''.join(checksums).encode()
            member = tarfile.TarInfo(TOOL_ID+'/eso-hotpatch/RUNTIME-SHA256SUMS')
            member.size, member.mode = len(data), 0o644
            archive.addfile(member, io.BytesIO(data))
    if args.output.stat().st_size >= 2*1024**3:
        raise SystemExit('Archive exceeds GitHub individual asset limit; do not upload')
    print('Ready-to-use runtime packaged:', len(checksums), 'files;', args.output.stat().st_size, 'bytes')


if __name__ == '__main__':
    main()
