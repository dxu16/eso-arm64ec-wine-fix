# Sources, notices, and distribution

This package modifies the Wine DLL from the exact BNet1 Linux ARM64 runtime.
Wine remains under its existing LGPL-2.1-or-later terms. FEX, GE-Proton,
LLVM runtime components, BNet scripts, and other dependencies retain their
separate notices and licenses. The full compiled runtime retains its
upstream license files and BNet's collected `bnet/licenses/` directory.

Copied upstream notices are preserved in this repository's `LICENSES/`.
The root MIT license covers only new helpers and documentation, not the
compiled DLL, copied licenses, third-party sources, or runtime components.

## Corresponding source assets

The local release-assets directory includes these unchanged source archives
from the [BNet1 release](https://github.com/mrdidit/bnet-arm/releases/tag/BNet1):

| Asset | SHA256 |
| --- | --- |
| Bnet1-component-sources.tar.gz | `480d39c59c4a9d755334379d7545fa844b88ea705c9e92d7e699026730e068e7` |
| GE-Proton11-7-upstream-sources.tar.zst | `62700f9eedaf153705193f2d72964f986eb56f45672ec86033a945cd4e89599f` |
| GE-Proton11-7-extras-sources.tar.zst | `8a972f75e4ebc9eea5a874d69988d5a33a30265a2b7efa147c914762dde1f142` |

Publish these source assets alongside the compiled runtime and this repository
snapshot, retaining the supplied licenses, attribution, patch manifest, and
transformation script. Branch links alone are not a substitute for the exact
source assets. The fetch script can restore missing local source archives
and refuses files whose hashes differ.

BNet's pinned source/build identities are retained in
`evidence/bnet-source-pins.json`. They identify GE-Proton11-7, the Wine base
and GameNative patch revision, and FEX-2610 with BNet's existing patch series.
No additional FEX patch is part of the ESO correction.

## Credits

- mrdidit: BNet Linux ARM64 build, packaging, provenance, and validation work.
- Dmage22: original Blizzard compatibility changes credited by BNet.
- GameNative, tarikbc, and Utkarsh Dalal: integration and existing Wine/FEX changes credited by BNet.
- GloriousEggroll and GE-Proton contributors: base compatibility tool.
- Wine, FEX, LLVM, Proton, and dependency contributors: underlying components.

The new ESO diagnosis and binary transformation are documented here as a
experimental compatibility project. They are not endorsed by, or
submitted as contributions to, any of the above projects.
