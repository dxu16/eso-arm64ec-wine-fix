#!/usr/bin/env python3
"""Check project files for common credentials and device-specific data before publication.

This complements manual review. Upstream copyright/contact notices are retained;
they are not treated as private device data. Large pinned source assets are
verified by hash separately and are not scanned as project-authored content.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SECRET = re.compile(rb'-----BEGIN (?:OPENSSH |RSA |DSA |EC |ENCRYPTED )?PRIVATE KEY-----|github_pat_[A-Za-z0-9_]{30,}|gh[pousr]_[A-Za-z0-9]{30,}')
HOME = re.compile(rb'/(?:var/)?home/[A-Za-z0-9_.-]+/|[A-Za-z]:[\\/]+Users[\\/]+[A-Za-z0-9_.-]+[\\/]', re.I)
PRIVATE_IP = re.compile(rb'\b(?:192\.168|10\.[0-9]{1,3})\.[0-9]{1,3}\.[0-9]{1,3}\b')
FORBIDDEN = {'authorized_keys', 'id_ed25519', 'id_rsa', 'loginusers.vdf', '.env'}


def main():
    failures = []
    count = 0
    for path in ROOT.rglob('*'):
        relative = path.relative_to(ROOT)
        if '.git' in relative.parts or 'release-assets' in relative.parts:
            continue
        if not path.is_file():
            continue
        count += 1
        if path.name in FORBIDDEN or '__pycache__' in relative.parts or path.suffix in {'.pyc', '.pyo', '.reg', '.log'}:
            failures.append((relative.as_posix(), 'forbidden generated/private file'))
        data = path.read_bytes()
        if SECRET.search(data):
            failures.append((relative.as_posix(), 'credential/private-key shape'))
        if 'LICENSES' not in relative.parts and path.suffix != '.dll':
            if HOME.search(data):
                failures.append((relative.as_posix(), 'resolved user-home path'))
            if PRIVATE_IP.search(data):
                failures.append((relative.as_posix(), 'private-network address'))
    if failures:
        for name, reason in failures:
            print(name + ': ' + reason, file=sys.stderr)
        raise SystemExit(1)
    print('PASS: public-content checks across', count, 'project files; upstream attribution retained')


if __name__ == '__main__':
    main()
