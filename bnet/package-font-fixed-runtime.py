#!/usr/bin/env python3
"""Create the v0.4.1 font-fixed runtime from the exact public v0.4.0 archive."""
from pathlib import Path
import argparse
import gzip
import hashlib
import importlib.util
import io
import tarfile
import runtime

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('proton_font_init', HERE / 'patch-proton-font-init.py')
patch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(patch)
INPUT_SHA256 = '7cfb4061e166587d7b4cfba00fd32e4b1b48d6c27119cebf3478bf42dd6c1fe6'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if args.output.exists() or args.input.resolve() == args.output.resolve():
        parser.error('Choose a new, separate output archive')
    with args.input.open('rb') as source:
        if hashlib.file_digest(source, 'sha256').hexdigest() != INPUT_SHA256:
            parser.error('Expected the exact public v0.4.0 archive')
    digests = {}
    root = HERE.parent
    replacements = {'eso-bnet/README.md': (root / 'README.md').read_bytes()}
    for path in (root / 'docs').rglob('*'):
        if path.is_file():
            replacements['eso-bnet/docs/' + path.relative_to(root / 'docs').as_posix()] = path.read_bytes()
    replacements['README-ESO.txt'] = b'GE-Proton11-7 ESO BNet ARM64 v0.4.1. Extract this tool into ~/.local/share/Steam/compatibilitytools.d/ and restart Steam. Installation and existing-prefix font repair: eso-bnet/docs/INSTALL.md. Release and sources: https://github.com/dxu16/eso-arm64ec-wine-fix/releases/tag/v0.4.1\n'
    with args.output.open('xb') as output, gzip.GzipFile(filename='', fileobj=output, mode='wb', compresslevel=3, mtime=0) as compressed, tarfile.open(fileobj=compressed, mode='w|') as dest, tarfile.open(args.input, 'r|gz') as source:
        def add(name, data):
            member = tarfile.TarInfo(runtime.TOOL_ID + '/' + name)
            member.mode = 0o644
            member.size = len(data)
            dest.addfile(member, io.BytesIO(data))
            digests[name] = hashlib.sha256(data).hexdigest()
        for member in source:
            name = runtime.safe_name(member.name)
            if name == runtime.INDEX:
                continue
            if not member.isfile():
                dest.addfile(member)
                continue
            data = source.extractfile(member).read()
            if name == 'proton':
                data = patch.transform(data)
            elif name == 'version':
                data = b'1789520806 GE-Proton11-7-ESO-BNet-arm64-v0.4.1\n'
            elif name == 'RUNTIME-SOURCES.txt':
                data = data.replace(b'v0.4.0', b'v0.4.1')
                data += b'\nFont initialization fix: additional preferred source is bundled in eso-bnet/patch-proton-font-init.py. No Wine/FEX binaries changed.\n'
            elif name in replacements:
                data = replacements.pop(name)
            member.size = len(data)
            dest.addfile(member, io.BytesIO(data))
            digests[name] = hashlib.sha256(data).hexdigest()
        for name in ['patch-proton-font-init.py', 'repair-launcher-fonts.py', 'package-font-fixed-runtime.py']:
            add('eso-bnet/' + name, (HERE / name).read_bytes())
        for name, data in replacements.items():
            add(name, data)
        add('README-FONT-FIX.txt', b'This v0.4.1 runtime exposes bundled fonts before Wine initializes a fresh template. It fixes the reproduced ESO launcher stack overflow with a new prefix. Existing affected prefixes can be repaired, with ESO closed, using: python3 eso-bnet/repair-launcher-fonts.py /path/to/steamapps/compatdata/306130\nThe helper backs up system.reg and downloads no fonts. Original Wine/FEX components and ESO DLL corrections are unchanged.\n')
        index = ''.join(value + '  ' + name + '\n' for name, value in sorted(digests.items())).encode()
        add(runtime.INDEX, index)
    print(runtime.verify(args.output))


if __name__ == '__main__':
    main()
