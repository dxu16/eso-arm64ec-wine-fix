# Current BNet-based runtime

This directory contains the BNet runtime sources, including the fresh-prefix
font fix included in v0.4.1. These scripts are maintained in the main repository;
they are also bundled in the complete runtime. The repository's older `scripts/`
and `bin/` preserve the Valve-based v0.3.0 reproduction path.

- `verify.py`: verify both bundled BNet ESO DLLs and exact post-link reproduction.
- `reproduce.py`: transform only the pinned input DLLs into separate new outputs.
- `runtime.py`: independently verify the full release archive without execution.
- `package.py`: package a retained, checksum-indexed BNet comparison runtime snapshot.
- `source-manifest.json`: hashes and original URLs of the three corresponding-source archives.
- `upstream-source-pins.json` and `patches/`: original BNet pins and attributed patches.
- [`repair-launcher-fonts.py`](repair-launcher-fonts.py): repair an idle existing prefix's missing font registrations, with a registry backup.
- [`patch-proton-font-init.py`](patch-proton-font-init.py): reproduce the automatic font-initialization change from the exact v0.4.0 Proton launcher into a new output file.
- [`package-font-fixed-runtime.py`](package-font-fixed-runtime.py): create and independently verify the complete fixed runtime from the public v0.4.0 runtime archive.
- [`test_font_repair.py`](test_font_repair.py): test backup preservation, idempotence and refusal of unsafe repair inputs; runs in the repository's verification workflow.

## Build the fixed runtime from a source checkout

With Python 3.11 or newer and the original public v0.4.0 archive available, run
from the repository root:

```sh
python3 -B bnet/package-font-fixed-runtime.py GE-Proton11-7-ESO-BNet-arm64.tar.gz GE-Proton11-7-ESO-BNet-arm64-fontfix-v0.4.1.tar.gz
```

No separate release-only script, compiler, Python dependency installation or
configured game prefix is needed. The script checks the exact input archive,
reproduces the launcher change, includes the additional sources, regenerates
checksums and verifies the output. It does not rebuild Wine or FEX; their pinned
binaries are preserved. See [BUILD.md](../docs/BUILD.md) for the complete recipe.

The full runtime is derived from [mrdidit's BNet1](https://github.com/mrdidit/bnet-arm).
Wine-derived transformations, patches and assembly retain LGPL terms. Original
project helpers retain the repository license; third-party code retains its own terms.

See [installation](../docs/INSTALL.md), [validation](../docs/VALIDATION.md), and
[source/license details](../docs/SOURCES-AND-LICENSES.md).
