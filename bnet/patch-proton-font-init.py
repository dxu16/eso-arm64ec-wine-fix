#!/usr/bin/env python3
"""Reproduce the fresh-template font initialization fix for the v0.4.0 launcher."""
import argparse
import hashlib
from pathlib import Path

INPUT_SHA256 = 'c0fe398829c78c82b26d39c20fbeb6b28d1e46941723962d794d7e5f67d402be'
OLD = b'''            if self.missing_default_prefix():
                #make default prefix
                local_env["WINEPREFIX"] = self.default_pfx_dir
'''
NEW = b'''            if self.missing_default_prefix():
                # Make bundled fonts visible before wineboot builds the font
                # registry. Adding symlinks only to the game prefix afterwards
                # leaves these fonts unregistered in a regenerated template.
                windows_fonts = os.path.join(self.default_pfx_dir, "drive_c/windows/Fonts")
                makedirs(windows_fonts)
                for fonts_dir in (self.fonts_dir, self.wine_fonts_dir):
                    for font in os.listdir(fonts_dir):
                        if not font.endswith((".ttf", ".ttc")):
                            continue
                        target = os.path.join(windows_fonts, font)
                        if not os.path.lexists(target):
                            os.symlink(os.path.join(fonts_dir, font), target)
                #make default prefix
                local_env["WINEPREFIX"] = self.default_pfx_dir
'''


def transform(data):
    if hashlib.sha256(data).hexdigest() != INPUT_SHA256 or data.count(OLD) != 1:
        raise ValueError('Unrecognized Proton launcher; expected the exact v0.4.0 input')
    result = data.replace(OLD, NEW, 1)
    compile(result, 'proton', 'exec')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    if args.output.exists() or args.input.resolve() == args.output.resolve():
        parser.error('Choose a new, separate output file')
    result = transform(args.input.read_bytes())
    with args.output.open('xb') as output:
        output.write(result)
    args.output.chmod(args.input.stat().st_mode & 0o777)
    print(hashlib.sha256(result).hexdigest())
