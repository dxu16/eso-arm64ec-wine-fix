#!/usr/bin/env python3
"""Download and hash-check the ready-runtime component source archives."""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--destination',type=Path,default=Path('runtime-sources'))
args=parser.parse_args()
args.destination.mkdir(parents=True,exist_ok=True)
for row in json.loads((ROOT/'runtime-source-manifest.json').read_text())['sources']:
    path=args.destination/row['name']
    if Path(row['name']).name != row['name']:
        raise SystemExit('Invalid source archive name')
    if not path.exists():
        request=urllib.request.Request(row['url'],headers={'User-Agent':'ESO-runtime-source-fetcher'})
        temporary=path.with_suffix(path.suffix+'.partial')
        with urllib.request.urlopen(request,timeout=180) as source,temporary.open('wb') as output:
            for block in iter(lambda:source.read(1024*1024),b''):
                output.write(block)
        temporary.replace(path)
    digest=hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda:source.read(1024*1024),b''):
            digest.update(block)
    if digest.hexdigest()!=row['sha256'] or path.stat().st_size!=row['size_bytes']:
        raise SystemExit('Source checksum mismatch: '+path.name)
    print('Verified:',path.name)
