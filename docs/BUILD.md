# Exact BNet ESO DLL reproduction

The base is the original [BNet1 runtime](https://github.com/mrdidit/bnet-arm/releases/tag/BNet1), itself based on GE-Proton11-7 ARM64. Component revisions, patch order and authors are recorded in `bnet/upstream-source-pins.json`.

Two Wine DLLs receive deterministic post-link corrections. Wine was not recompiled. Recompiling the whole upstream base byte-for-byte has not been demonstrated.

| DLL | Original SHA256 | Patched SHA256 |
| --- | --- | --- |
| kernel32 | `fed36267d61204658b96a976e4cf19ab1053c49a466ca58c2bde6089148773cb` | `5b9c2d116f93a307e7b69c31544e52b7a5081fa7caa384020b1c09f948664d5b` |
| ntdll | `e28f25f21ecf34a32ee2ce24672f023e436da08a88a01c6d4e93757633c9ba47` | `5da92139e0e34111acf952b4d7ba590da09d34fdb9e99b68086c6081bcda16ac` |

```bash
python3 -B bnet/reproduce.py bnet kernel32 original-kernel32.dll new-kernel32.dll
python3 -B bnet/reproduce.py bnet ntdll original-ntdll.dll new-ntdll.dll
python3 -B bnet/verify.py
```

Outputs must be new paths. The recipe rejects unrecognized input hashes, unexpected layouts, aliases and existing outputs, including under Python `-O`.

kernel32 gets 796 identity-LEA prologs inside existing 16-byte imported-entry slots, preserving addresses and import targets. The ntdll change occupies 36 different bytes across its branch, native helper and ARM64EC code-range size. The helper was independently assembled and matched byte-for-byte. Import/export tables are preserved. `bnet/helper-reference.s` and the two change manifests record the exact transformation.

`bnet/wine-arm64ec-hotpatch-prolog.patch` is the equivalent Wine source change. It was checked to apply to the prepared BNet source but was not compiled into these binaries. The preferred source for the post-link transformations is `bnet/reproduce.py` plus its manifests.

Package a runtime snapshot with `python3 -B bnet/package.py --input runtime-input.tar --output GE-Proton11-7-ESO-BNet-arm64.tar.gz`. Input must contain exactly the retained BNet comparison tool, not a prefix or investigation directory. The packager checks core hashes, removes generated templates/caches, replaces comparison metadata with release metadata, preserves notices, creates internal checksums, and calls the independent archive verifier. Corresponding-source assets are indexed in `bnet/source-manifest.json`.

The v0.3.0 Valve reproduction material remains under `scripts/`, `bin/`, and [legacy build notes](legacy-valve/BUILD.md). Its hashes and offsets must not be used for BNet.
