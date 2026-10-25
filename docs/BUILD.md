# Exact DLL reproduction

## What was built?

The kernel32 file is Valve's precompiled Wine kernel32 after a deterministic **post-link binary transformation**. Wine was not recompiled. There is not yet a source-level Wine/LLVM linker patch for this change.

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
python3 scripts/package-overlay.py --output release-assets/Proton-11.0-ESO-Performance-Hotpatch-arm64-overlay.tar.gz
```

This collects the compiled DLL, transformation, installer, launcher, documentation, sanitized evidence, and notices. It excludes runtime/prefix directories, private backups, bytecode caches, and release source archives. It creates internal per-file checksums. The separate release SHA256SUMS and release-manifest.json describe outer downloads; they are not recursively embedded in their own overlay.

The installed full compatibility tool is assembled locally from the official Steam runtime. The overlay does not redistribute Valve's unchanged binary bundle.

## Ntdll performance correction (default since v0.3.0)

Input SHA256: `5bab1f413ea1032ba9d1fd8a500b83d0248092e1911ba487a96d797fe062b71f`.
Output SHA256: `74e45da0005fa0c890bdb3cc78e14af1d590fc8e22bc51a633755e0f47426eb2`.

Run `python3 scripts/reproduce-ntdll-performance.py original-ntdll.dll new-ntdll.dll`.
The script refuses unknown input, aliases, existing output, layout mismatches, or an unexpected output hash, including under Python `-O`.

The exact 36 changed bytes occupy three manifest spans: a branch at RVA 0xc9278, a 40-byte native helper in zero-filled ARM64EC text padding at 0xf0840, and the ARM64EC code-range size. File size and import/export tables are unchanged. The helper recognizes the exact eight-byte identity LEA, advances past it, and resumes Wine's existing import-jump recognition. Other entries resume the original fast-forward comparison. It uses existing scratch registers and leaves the stack unchanged.

`patches/ntdll-performance.json` records every changed span. `patches/ntdll-helper-reference.s` independently assembles the helper instructions. `patches/wine-arm64ec-hotpatch-prolog.patch` is an equivalent source-level Wine change, checked to apply to the pinned source but not compiled into the distributed binary. The preferred binary modification recipe and native assembly reference are supplied alongside the full original Wine source. The verifier reconstructs the original ntdll, reproduces the shipped output, checks helper encodings, and exercises rejection cases.

## Package a full ready-to-use tool

After preparing a separate tool with the installer, add matching component notices, their source index, and RUNTIME-SOURCES.txt, then run `python3 scripts/package-runtime.py --tool /path/to/prepared/tool --output ready-tool.tar.gz`. The packager verifies both DLLs, excludes generated prefixes and caches, removes their SteamPipe directory fixups, rejects private-home/credential data and external symlinks, canonicalizes archive metadata, and includes per-file checksums. Verify with `python3 scripts/verify-runtime.py ready-tool.tar.gz`. See READY-TO-USE.md for the source archive and distribution format.
