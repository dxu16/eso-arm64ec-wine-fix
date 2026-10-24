# ESO ARM64EC Wine fix v0.2.0 — official Proton base

This release replaces the BNet dependency with **Valve Proton 11.0-2e ARM64**, using the same kernel32 imported-export entry-layout correction.

## Result

The stock official runtime with a Steam-initialized ESO prefix reproduced 0x1100 at 305.376 seconds and reported 28 API entrypoints. With only the kernel32 correction, the same setup reported zero entries, had no observed shutdown thread, reached the animated title screen, and survived a 420-second timeout. The packaged installer/launcher survived another 420-second timeout.

FEX, ntdll, kernelbase, the WOW64 translator, and the rest of the official base are unchanged. BNet is not required for this measured failure.

## Download and install

Download the **precompiled overlay** and SHA256SUMS. The unchanged full runtime is supplied by Steam; the installer creates a separate complete compatibility tool from it.

1. Install Proton 11.0 (ARM64) in Steam; supported version: 1791559733 proton-11.0-2e-arm64.
2. Launch ESO once through Steam to initialize its prefix, then close it.
3. Extract the overlay, enter eso-arm64ec-wine-fix, and run:

```bash
python3 scripts/verify.py
python3 scripts/install.py
bash scripts/launch-eso.sh
```

No compiler or BNet download is needed. Restart Steam to see **Proton 11.0 ESO Hotpatch (official base, ARM64, experimental)**. The controlled test uses a separate clone of the Steam-initialized prefix; the source prefix and official runtime are preserved.

The release includes exact Wine sources, Proton build recipes, and the complete post-link transformation. **Wine was not recompiled:** the included script reproduces the supplied DLL from the pinned precompiled baseline.

## Limits and privacy

Login, gameplay, long sessions, other builds, performance and account safety remain untested. Modified bytes can be noticed by other checks or future updates. This is not a guarantee of approval or protection from enforcement.

The earlier BNet release was removed. Its scrubbed source history remains at v0.1.0-experimental. The new overlay contains no device prefixes, raw registries, process dumps, personal paths, SSH material or bytecode caches. Upstream notices and public author attribution are preserved.

Patched kernel32 SHA256:

```text
dbf5fa3a80204259f8e42e9a4ebcbdd6769f3f86301aa9da39f22797e0e40257
```
