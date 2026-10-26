#!/usr/bin/env python3
# Legacy Valve v0.3 helper; recommended BNet installation: docs/INSTALL.md.
"""Create a separate ESO tool from the exact tested Valve Proton 11 ARM64 build."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
TOOL_ID = 'Proton-11.0-ESO-Performance-Hotpatch-arm64'
PATCHED = 'dbf5fa3a80204259f8e42e9a4ebcbdd6769f3f86301aa9da39f22797e0e40257'
PATCHED_DLLS = {'kernel32.dll': ('kernel32-eso-hotpatch.dll', PATCHED),
                'ntdll.dll': ('ntdll-eso-performance.dll', '74e45da0005fa0c890bdb3cc78e14af1d590fc8e22bc51a633755e0f47426eb2')}
BASE_HASHES = {
    'kernel32.dll': '472d5a6b9906e90262dfacb5ed7ced11c76e8dbdd95037e424cf4fd7412299c6',
    'libarm64ecfex.dll': 'fb9e057a719540626a1399c8b91501ebc57cdde7a623d280616a67234808c3fe',
    'libwow64fex.dll': 'e7cdc7e0df3f1f222238cb7d16ac35257bfcd6ecf417d7ac7fdf2083a581d948',
    'ntdll.dll': '5bab1f413ea1032ba9d1fd8a500b83d0248092e1911ba487a96d797fe062b71f',
    'kernelbase.dll': '79c431521972199646099466da254993e278f7e2053245dfb741f116cd96586c',
}
BASE_UNIX_HASHES = {
    'libarm64ecfex.so': 'dc8f21f75ee11c3829b346d5a8d60ee87d24091f5e6ed901b5c36c739832ac53',
    'libwow64fex.so': '257041413ae02eb5e2ba31fd16d991478f3a3b53f8ed48b3cc356e42f77649be',
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, default=Path.home() / '.local/share/Steam/steamapps/common/Proton 11.0 (ARM64)')
    parser.add_argument('--destination', type=Path, default=Path.home() / '.local/share/Steam/compatibilitytools.d' / TOOL_ID)
    args = parser.parse_args()
    base, destination = args.base.expanduser().resolve(), args.destination.expanduser().resolve()
    if destination.exists() or args.destination.is_symlink():
        parser.error('Destination must not exist; nothing will be overwritten.')
    if destination == base or base in destination.parents:
        parser.error('Destination must be outside the base runtime.')
    for name, (asset, expected) in PATCHED_DLLS.items():
        if digest(ROOT / 'bin' / asset) != expected:
            parser.error('Bundled DLL checksum failed: ' + name)
    if (base / 'version').read_text().strip() != '1791559733 proton-11.0-2e-arm64':
        parser.error('Only the tested Valve Proton 11.0-2e ARM64 build is supported.')
    for name, expected in BASE_HASHES.items():
        if digest(base / 'files/lib/wine/aarch64-windows' / name) != expected:
            parser.error(f'Unrecognized baseline {name}; only Valve Proton 11.0-2e ARM64 is supported.')
    for name, expected in BASE_UNIX_HASHES.items():
        if digest(base / 'files/lib/wine/aarch64-unix' / name) != expected:
            parser.error(f'Unrecognized baseline Unix component {name}.')
    if not (base / 'proton').is_file():
        parser.error('Base does not contain the Proton launcher.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    print('Copying base runtime into', destination, flush=True)
    shutil.copytree(base, destination, symlinks=True)
    for name, (asset, expected) in PATCHED_DLLS.items():
        compiled = ROOT / 'bin' / asset
        library = destination / 'files/lib/wine/aarch64-windows' / name
        for target in [library, destination / 'files/share/default_pfx_arm64/drive_c/windows/system32' / name]:
            if not target.parent.resolve().is_relative_to(destination):
                raise SystemExit('Unexpected external directory symlink')
            if target.is_symlink() and target.resolve() == library.resolve():
                if digest(target) != expected:
                    raise SystemExit('Template symlink did not resolve to the patched DLL')
                continue
            if digest(target) != BASE_HASHES[name]:
                raise SystemExit('Unexpected template DLL; incomplete destination retained: ' + str(target))
            target.unlink()  # Break links before copying, preserving the source runtime.
            shutil.copy2(compiled, target)
    metadata = destination / 'compatibilitytool.vdf'
    metadata.write_text('"compatibilitytools"\n{\n "compat_tools"\n {\n  "' + TOOL_ID +
                        '"\n  {\n   "install_path" "."\n   "display_name" "Proton 11.0 ESO Performance Hotpatch (ARM64, experimental)"\n'
                        '   "from_oslist" "windows"\n   "to_oslist" "linux"\n  }\n }\n}\n')
    notice = destination / 'eso-hotpatch'
    notice.mkdir(exist_ok=True)
    for directory in ['docs', 'scripts', 'patches', 'bin', 'evidence', 'LICENSES']:
        shutil.copytree(ROOT / directory, notice / directory, dirs_exist_ok=True)
    for name in ['README.md', 'LICENSE', 'source-manifest.json']:
        shutil.copy2(ROOT / name, notice / name)
    (notice / 'component-hashes.json').write_text(json.dumps({'baseline': BASE_HASHES, 'baseline_unix': BASE_UNIX_HASHES, 'patched_dlls': {name: value[1] for name, value in PATCHED_DLLS.items()}}, indent=2) + '\n')
    print('Installed separate experimental tool. Base runtime and game prefix unchanged.')


if __name__ == '__main__':
    main()
