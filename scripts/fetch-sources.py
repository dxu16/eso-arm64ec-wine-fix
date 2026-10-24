#!/usr/bin/env python3
"""Download unchanged corresponding source assets from the pinned BNet1 release."""
import hashlib
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
ASSETS = {
    'Bnet1-component-sources.tar.gz': '480d39c59c4a9d755334379d7545fa844b88ea705c9e92d7e699026730e068e7',
    'GE-Proton11-7-upstream-sources.tar.zst': '62700f9eedaf153705193f2d72964f986eb56f45672ec86033a945cd4e89599f',
    'GE-Proton11-7-extras-sources.tar.zst': '8a972f75e4ebc9eea5a874d69988d5a33a30265a2b7efa147c914762dde1f142',
}


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    destination = ROOT / 'release-assets'
    destination.mkdir(exist_ok=True)
    for name, expected in ASSETS.items():
        path = destination / name
        if path.exists():
            if sha256(path) != expected:
                raise SystemExit(f'Existing asset has wrong hash: {path}')
            print('Verified', name, flush=True)
            continue
        temporary = destination / (name + '.tmp')
        if temporary.exists():
            raise SystemExit(f'Remove or inspect incomplete download first: {temporary}')
        url = 'https://github.com/mrdidit/bnet-arm/releases/download/BNet1/' + name
        print('Downloading', name, flush=True)
        request = urllib.request.Request(url, headers={'User-Agent': 'eso-arm64ec-wine-fix'})
        with urllib.request.urlopen(request, timeout=120) as source, temporary.open('xb') as output:
            for block in iter(lambda: source.read(1024 * 1024), b''):
                output.write(block)
        if sha256(temporary) != expected:
            raise SystemExit(f'Download failed checksum; retained for inspection: {temporary}')
        temporary.rename(path)
        print('Verified', name, flush=True)


if __name__ == '__main__':
    main()
