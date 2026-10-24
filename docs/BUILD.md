# Reproduction and provenance

## Supported binary input

The baseline is `files/lib/wine/aarch64-windows/kernel32.dll` from BNet1:

```text
fed36267d61204658b96a976e4cf19ab1053c49a466ca58c2bde6089148773cb
```

The tested ARM64X output is:

```text
5b9c2d116f93a307e7b69c31544e52b7a5081fa7caa384020b1c09f948664d5b
```

Run from the repository root with a new output filename:

```bash
python3 scripts/reproduce-kernel32-hotpatch.py original-kernel32.dll new-kernel32.dll
python3 scripts/verify.py
```

The input is never written. Existing outputs, input/output aliasing, unknown
baseline hashes, mismatching bytes, and changed import-slot targets are
rejected. Guards remain enabled under Python's `-O` option.

Verification independently reverses the recorded replacements to recover
the original hash, runs the actual CLI transformation, compares its output
byte-for-byte with the compiled DLL, and exercises rejection cases. This
requires no ESO installation, remote access, or third-party Python packages.

## Baseline source build

`evidence/bnet-source-pins.json` retains BNet's source revisions and patch
identities. The prepared Wine/FEX source and baseline build recipes are in
`Bnet1-component-sources.tar.gz`. The other two source archives cover the
unchanged GE base and dependencies. They are obtained with:

```bash
python3 scripts/fetch-sources.py
```

The tested DLL was made by transforming the original BNet binary, not by
substituting an independently rebuilt Wine. Building the baseline sources
is useful for development but has not been established to reproduce BNet's
binary byte-for-byte. A newly built kernel32 with another hash is rejected.

The patch has not yet been expressed as a source-level Wine/LLVM linker
change. The manifest and transformation script are the complete recipe for
this binary modification; they do not contain proprietary game code.

## Complete runtime archive

The compiled release is a copy of the tested BNet runtime with two DLL copies
updated: the ARM64 runtime kernel32 and its default ARM64 prefix template.
Its compatibility tool ID/display name are distinct. FEX, ntdll, kernelbase,
and the rest of the base runtime payload retain their baseline versions.
Baseline BNet build records describe the base; this repository's records
describe the additional kernel32 transformation.

Original tested BNet hashes:

| File | SHA256 |
| --- | --- |
| libarm64ecfex.dll | `27e2b27b7c11e847ac4687614ebcedc02854938427b43eefb5e64b099bad2733` |
| ntdll.dll | `e28f25f21ecf34a32ee2ce24672f023e436da08a88a01c6d4e93757633c9ba47` |
| kernelbase.dll | `37530751e58f312a2f6aa0d72a9005b86d5e75c347b3c7ec52dca1051f33f5f1` |

Compiled tool and source asset checksums are in `release-manifest.json` and
`release-assets/SHA256SUMS`. Archive compression/timestamps are not claimed
to be reproducible; the patched DLL itself is exactly reproducible.
