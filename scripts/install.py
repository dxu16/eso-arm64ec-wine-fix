#!/usr/bin/env python3
"""Create a separate ESO compatibility tool from the exact tested BNet build."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
TOOL_ID = 'GE-Proton11-7-ESO-Hotpatch-arm64'
PATCHED = '5b9c2d116f93a307e7b69c31544e52b7a5081fa7caa384020b1c09f948664d5b'
BASE_HASHES = {
    'kernel32.dll': 'fed36267d61204658b96a976e4cf19ab1053c49a466ca58c2bde6089148773cb',
    'libarm64ecfex.dll': '27e2b27b7c11e847ac4687614ebcedc02854938427b43eefb5e64b099bad2733',
    'ntdll.dll': 'e28f25f21ecf34a32ee2ce24672f023e436da08a88a01c6d4e93757633c9ba47',
    'kernelbase.dll': '37530751e58f312a2f6aa0d72a9005b86d5e75c347b3c7ec52dca1051f33f5f1',
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--destination', type=Path, default=Path.home() / '.local/share/Steam/compatibilitytools.d' / TOOL_ID)
    args = parser.parse_args()
    base, destination = args.base.expanduser().resolve(), args.destination.expanduser().resolve()
    if destination.exists() or args.destination.is_symlink():
        parser.error('Destination must not exist; nothing will be overwritten.')
    if destination == base or base in destination.parents:
        parser.error('Destination must be outside the base runtime.')
    compiled = ROOT / 'bin/kernel32-eso-hotpatch.dll'
    if digest(compiled) != PATCHED:
        parser.error('Bundled DLL checksum failed.')
    for name, expected in BASE_HASHES.items():
        if digest(base / 'files/lib/wine/aarch64-windows' / name) != expected:
            parser.error(f'Unrecognized baseline {name}; only the exact BNet1 build is supported.')
    if not (base / 'proton').is_file():
        parser.error('Base does not contain the Proton launcher.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    print('Copying base runtime into', destination, flush=True)
    shutil.copytree(base, destination, symlinks=True)
    for relative in ['files/lib/wine/aarch64-windows/kernel32.dll',
                     'files/share/default_pfx_arm64/drive_c/windows/system32/kernel32.dll']:
        target = destination / relative
        if not target.parent.resolve().is_relative_to(destination):
            raise SystemExit(f'Unexpected external directory symlink: {target.parent}')
        if digest(target) != BASE_HASHES['kernel32.dll']:
            raise SystemExit(f'Unexpected template DLL. Incomplete destination retained: {target}')
        target.unlink()  # Do not write through a hardlink or symlink into the base.
        shutil.copy2(compiled, target)
    metadata = destination / 'compatibilitytool.vdf'
    metadata.write_text('"compatibilitytools"\n{\n "compat_tools"\n {\n  "' + TOOL_ID +
                        '"\n  {\n   "install_path" "."\n   "display_name" "GE-Proton11-7-ESO Hotpatch (ARM64, experimental)"\n'
                        '   "from_oslist" "windows"\n   "to_oslist" "linux"\n  }\n }\n}\n')
    notice = destination / 'eso-hotpatch'
    notice.mkdir(exist_ok=True)
    for directory in ['docs', 'scripts', 'patches', 'bin', 'evidence', 'LICENSES']:
        shutil.copytree(ROOT / directory, notice / directory, dirs_exist_ok=True)
    for name in ['README.md', 'LICENSE']:
        shutil.copy2(ROOT / name, notice / name)
    (notice / 'component-hashes.json').write_text(json.dumps({'baseline': BASE_HASHES, 'patched_kernel32': PATCHED}, indent=2) + '\n')
    print('Installed separate experimental tool. Base runtime and game prefix unchanged.')


if __name__ == '__main__':
    main()
