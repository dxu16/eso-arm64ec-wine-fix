#!/usr/bin/env python3
"""Fetch the exact official Wine sources and Proton root build recipes."""
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()

def main():
    destination = ROOT / 'release-assets'
    destination.mkdir(exist_ok=True)
    for row in json.loads((ROOT/'source-manifest.json').read_text())['assets']:
        path = destination / row['name']
        if path.exists():
            if digest(path) != row['sha256']:
                raise SystemExit('Existing source checksum failed: '+row['name'])
            print('Verified', row['name'], flush=True)
            continue
        temporary = destination / (row['name']+'.tmp')
        if temporary.exists():
            raise SystemExit('Incomplete download exists; inspect it first: '+str(temporary))
        print('Downloading', row['name'], flush=True)
        request = urllib.request.Request(row['url'], headers={'User-Agent':'eso-official-proton-source-fetch'})
        with urllib.request.urlopen(request, timeout=120) as response, temporary.open('xb') as output:
            for block in iter(lambda: response.read(1024*1024), b''):
                output.write(block)
        if digest(temporary) != row['sha256']:
            raise SystemExit('Source checksum failed: '+row['name'])
        temporary.rename(path)
        print('Verified', row['name'], flush=True)

if __name__ == '__main__':
    main()
