# Current BNet-based runtime

This directory is the v0.4.0 default. The repository's older `scripts/` and
`bin/` preserve the Valve-based v0.3.0 reproduction path.

- `verify.py`: verify both bundled BNet ESO DLLs and exact post-link reproduction.
- `reproduce.py`: transform only the pinned input DLLs into separate new outputs.
- `runtime.py`: independently verify the full release archive without execution.
- `package.py`: package a retained, checksum-indexed BNet comparison runtime snapshot.
- `source-manifest.json`: hashes and original URLs of the three corresponding-source archives.
- `upstream-source-pins.json` and `patches/`: original BNet pins and attributed patches.

The full runtime is derived from [mrdidit's BNet1](https://github.com/mrdidit/bnet-arm).
Wine-derived transformations, patches and assembly retain LGPL terms. Original
project helpers retain the repository license; third-party code retains its own terms.

See [installation](../docs/INSTALL.md), [validation](../docs/VALIDATION.md), and
[source/license details](../docs/SOURCES-AND-LICENSES.md).
