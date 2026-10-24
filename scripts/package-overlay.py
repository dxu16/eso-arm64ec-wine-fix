#!/usr/bin/env python3
"""Package the precompiled patch/installer without a device runtime or prefix."""
import argparse
import gzip
import hashlib
import io
from pathlib import Path
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit('Output already exists; choose a new filename')
    subprocess.run([sys.executable, '-B', str(ROOT/'scripts/check-public-content.py')], cwd=ROOT, check=True)
    files = [ROOT/name for name in ['README.md', 'LICENSE', 'source-manifest.json']]
    for folder in ['bin', 'docs', 'scripts', 'patches', 'evidence', 'LICENSES']:
        files.extend(p for p in (ROOT/folder).rglob('*') if p.is_file())
    files = sorted(set(files))
    checksums = ''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(ROOT).as_posix()+'\n' for p in files).encode('utf-8')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('xb') as raw, gzip.GzipFile(filename='', fileobj=raw, mode='wb', compresslevel=6, mtime=0) as compressed:
        with tarfile.open(fileobj=compressed, mode='w|') as archive:
            for path in files:
                data = path.read_bytes()
                member = tarfile.TarInfo('eso-arm64ec-wine-fix/'+path.relative_to(ROOT).as_posix())
                member.size = len(data)
                member.mode = 0o755 if path.suffix in {'.py', '.sh'} else 0o644
                member.mtime = 0
                archive.addfile(member, io.BytesIO(data))
            member = tarfile.TarInfo('eso-arm64ec-wine-fix/SHA256SUMS')
            member.size, member.mode, member.mtime = len(checksums), 0o644, 0
            archive.addfile(member, io.BytesIO(checksums))
    print('Wrote precompiled overlay:', args.output, args.output.stat().st_size, 'bytes')


if __name__ == '__main__':
    main()
