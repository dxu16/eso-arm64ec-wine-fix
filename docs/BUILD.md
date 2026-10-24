# Exact DLL reproduction

## What was built?

The shipped file is Valve's precompiled Wine kernel32 after a deterministic **post-link binary transformation**. Wine was not recompiled. There is not yet a source-level Wine/LLVM linker patch for this change.

Input: `files/lib/wine/aarch64-windows/kernel32.dll` from Steam's `1791559733 proton-11.0-2e-arm64`.

```text
Input SHA256:  472d5a6b9906e90262dfacb5ed7ced11c76e8dbdd95037e424cf4fd7412299c6
Output SHA256: dbf5fa3a80204259f8e42e9a4ebcbdd6769f3f86301aa9da39f22797e0e40257
```

## Reproduce

```bash
python3 scripts/reproduce-kernel32-hotpatch.py original-kernel32.dll new-kernel32.dll
python3 scripts/verify.py
```

No compiler or third-party Python modules are required. The script checks the exact input hash, verifies each original 16-byte slot, inserts the eight-byte `lea rsp,[rsp+0]` prolog, adjusts each RIP-relative jump displacement by -8, verifies the unchanged import-slot address, and checks the final output hash. It rejects unknown inputs, input/output aliasing, and an existing output; guards remain active under Python `-O`.

`patches/kernel32-hotpatch-thunks.json` is the complete change manifest. All 796 replacements preserve exported addresses and import targets. File size, native ARM64 instructions, import/export tables, and hybrid metadata are unchanged. `scripts/verify.py` independently reconstructs the original DLL from the compiled output, reproduces the patch through the CLI, and exercises rejection cases.

## Baseline source and build recipes

- [Valve Proton](https://github.com/ValveSoftware/Proton), tag `proton-11.0-2e`, commit `bc896217ffcd67f892f952b010f898fe7bd0f0a1`.
- [Valve Wine](https://github.com/ValveSoftware/wine), commit `e60892cc2398b0a83c332a2078c7b85e47bdb42b`.
- FEX submodule: `1cc4b93e7a71c883ec021b71359f136394dc1f3c`; its binaries are unchanged.

The release supplies the exact Wine source archive and Proton build-recipe archive. `source-manifest.json` records URLs and hashes; `scripts/fetch-sources.py` retrieves and verifies them. The Proton archive is the root build-recipe repository, not a recursively populated whole-runtime source bundle. Wine's full source is supplied separately for the modified DLL. Rebuilding Valve's original binary byte-for-byte has not been demonstrated; another input hash is intentionally rejected.

## Package the precompiled overlay

```bash
python3 scripts/package-overlay.py --output release-assets/Proton-11.0-ESO-Official-Hotpatch-arm64-overlay.tar.gz
```

This collects the compiled DLL, transformation, installer, launcher, documentation, sanitized evidence, and notices. It excludes runtime/prefix directories, private backups, bytecode caches, and release source archives. It creates internal per-file checksums. The separate release SHA256SUMS and release-manifest.json describe outer downloads; they are not recursively embedded in their own overlay.

The installed full compatibility tool is assembled locally from the official Steam runtime. The overlay does not redistribute Valve's unchanged binary bundle.
