#!/usr/bin/env python3
"""Register bundled fonts missing from an idle ESO Wine prefix. No downloads."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil

FONTS = {
    'Arial (TrueType)': 'arial.ttf',
    'Courier New (TrueType)': 'cour.ttf',
    'Marlett (TrueType)': 'marlett.ttf',
    'Microsoft YaHei (TrueType)': 'msyh.ttf',
    'Symbol (TrueType)': 'symbol.ttf',
    'Tahoma (TrueType)': 'tahoma.ttf',
    'Tahoma Bold (TrueType)': 'tahomabd.ttf',
    'Times New Roman (TrueType)': 'times.ttf',
    'Webdings (TrueType)': 'webdings.ttf',
    'Wingdings (TrueType)': 'wingding.ttf',
}
SECTION = r'[Software\\Microsoft\\Windows NT\\CurrentVersion\\Fonts]'


def repair(prefix):
    prefix = Path(prefix).expanduser().resolve(strict=True)
    if (prefix / 'pfx/system.reg').is_file():
        prefix = prefix / 'pfx'
    registry = prefix / 'system.reg'
    if not registry.is_file() or registry.is_symlink():
        raise ValueError('Expected a Wine prefix or Steam compatibility-data directory')
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit():
            continue
        try:
            env = (proc / 'environ').read_bytes().split(b'\0')
        except OSError:
            continue
        for item in env:
            if item.startswith(b'WINEPREFIX=') and Path(os.fsdecode(item[11:])).resolve() == prefix:
                raise ValueError('This prefix is in use. Close ESO and its Wine processes before retrying.')
    before = registry.read_bytes()
    text = before.decode('utf-8')
    if not text.startswith('WINE REGISTRY Version 2'):
        raise ValueError('Unrecognized Wine registry format')
    chunks = re.split(r'(?m)(?=^\[)', text)
    matches = [i for i, chunk in enumerate(chunks) if chunk.splitlines() and chunk.splitlines()[0].split(']')[0] + ']' == SECTION]
    if len(matches) > 1:
        raise ValueError('Duplicate font registry sections; no changes made')
    index = matches[0] if matches else None
    section = chunks[index] if index is not None else SECTION + '\n'
    registered = set(re.findall(r'^"([^"\n]+)"=', section, re.MULTILINE))
    additions = []
    for name, filename in FONTS.items():
        if name in registered:
            continue
        font = prefix / 'drive_c/windows/Fonts' / filename
        if not font.is_file() or font.stat().st_size < 12:
            raise ValueError('Bundled font is missing or its symlink is broken: ' + filename)
        additions.append((name, filename))
    if not additions:
        return {'changed': False, 'added': [], 'prefix': str(prefix)}
    section = section.rstrip() + '\n' + ''.join('"' + name + '"="' + filename + '"\n' for name, filename in additions) + '\n'
    if index is None:
        chunks.append(section)
    else:
        chunks[index] = section
    after = ''.join(chunks).encode('utf-8')
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    backup = registry.with_name('system.reg.before-eso-font-repair-' + stamp)
    shutil.copy2(registry, backup)
    if backup.read_bytes() != before or registry.read_bytes() != before:
        raise ValueError('Registry changed during backup; no repair applied')
    temporary = registry.with_name('system.reg.eso-font-repair-' + stamp + '.tmp')
    try:
        with temporary.open('xb') as output:
            output.write(after)
            output.flush()
            os.fsync(output.fileno())
        shutil.copymode(registry, temporary)
        os.replace(temporary, registry)
    finally:
        temporary.unlink(missing_ok=True)
    return {'changed': True, 'added': [name for name, _ in additions], 'backup': str(backup), 'prefix': str(prefix), 'registry_sha256': hashlib.sha256(after).hexdigest()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('prefix', type=Path, help='ESO compatibility-data directory, or its pfx directory')
    args = parser.parse_args()
    try:
        print(json.dumps(repair(args.prefix), indent=2))
    except (OSError, ValueError) as error:
        parser.exit(1, str(error) + '\n')
