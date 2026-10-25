# Official-base release assets

This directory's large files are excluded from Git. The current release ships:

- Proton-11.0-ESO-Performance-Hotpatch-arm64.tar.gz: full ready-to-extract compatibility tool.
- Proton-11.0-ESO-Performance-Hotpatch-arm64-runtime-sources.tar.gz: component sources, nested dependencies, patch recipes and source index.

- Proton-11.0-ESO-Performance-Hotpatch-arm64-overlay.tar.gz: both precompiled DLLs plus installer, launcher, recipe, documentation, and notices.
- Valve-Wine-e60892cc2398-sources.tar.gz: exact full source of the modified Wine component.
- Valve-Proton-bc896217ffcd-sources.tar.gz: exact Proton root source and build recipes; not a recursive entire-runtime source bundle.
- SHA256SUMS and release-manifest.json: outer download hashes and sizes.

The full archive includes the official base; the overlay obtains it from Steam. Steam supplies the external Linux runtime and FEX rootfs. No compiler is needed. The performance package is the default since v0.3.0-experimental. Private device backups and caches must never be included.
