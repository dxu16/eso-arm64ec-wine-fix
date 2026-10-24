# Local release assets

This directory is excluded from Git except for this README. Put these files
in a GitHub Release alongside the repository source archive:

- `GE-Proton11-7-ESO-Hotpatch-arm64.tar.gz`: complete compiled tool, not just a DLL.
- `Bnet1-component-sources.tar.gz`: exact prepared baseline Wine/FEX component sources and build recipes.
- `GE-Proton11-7-upstream-sources.tar.zst`: corresponding GE upstream sources.
- `GE-Proton11-7-extras-sources.tar.zst`: corresponding GE extra-component sources.
- `SHA256SUMS`: checksums for these release assets.

The three source archives are unchanged BNet1 release assets. The repository
supplies the deterministic transformation used to modify the baseline Wine
DLL. `python3 scripts/fetch-sources.py` downloads and verifies source archives
that are missing. Do not commit the multi-hundred-megabyte assets to Git.
