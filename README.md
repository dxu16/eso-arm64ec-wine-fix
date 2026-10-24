# ESO on official Proton 11 ARM64

An experimental Wine compatibility fix for ESO's repeatable **0x1100 self-exit after about 305 seconds**, tested on **Valve Proton 11.0-2e ARM64**.

**[Download the precompiled patch and installer](https://github.com/dxu16/eso-arm64ec-wine-fix/releases/download/v0.2.0-experimental/Proton-11.0-ESO-Official-Hotpatch-arm64-overlay.tar.gz)** · [Checksums](https://github.com/dxu16/eso-arm64ec-wine-fix/releases/download/v0.2.0-experimental/SHA256SUMS) · [Release and source archives](https://github.com/dxu16/eso-arm64ec-wine-fix/releases/tag/v0.2.0-experimental)

The installer clones your Steam-installed official runtime into a separate compatibility tool and applies the **already compiled kernel32.dll**. No compiler is needed. The unchanged Valve runtime is supplied by Steam rather than redistributed in this small overlay.

## What changed?

ESO's startup API-entry checks mistake legitimate ARM64EC imported-function jump thunks for hooks. The patch gives 796 existing kernel32 import-thunk slots the harmless entry prolog used by working x64 Wine. Function addresses, import-slot targets, native ARM64 code, and hybrid metadata are preserved.

Only Wine's kernel32 entry bytes change. **FEX, ntdll, kernelbase, and the WOW64 translator remain Valve's originals.** This does not modify ESO's executable or disable its checks.

## Result and limits

With copies of the same Steam-initialized ESO prefix:

| Configuration | Outcome |
| --- | --- |
| Official Proton 11.0-2e ARM64 | 28 API-entry reports; shutdown thread; 0x1100 exit at 305.376 seconds |
| Same runtime with only the kernel32 correction | Zero API-entry reports; no observed shutdown thread; animated title screen; survived 420-second timeout |
| Packaged installer and launcher | Zero API-entry reports; survived a second 420-second timeout |

**Login, server connection, gameplay, long sessions, other builds, and performance remain untested. Detection and account-safety risk are unknown.** Other integrity checks or future updates could notice or reject the changed entry bytes. The title-screen result is not a guarantee of approval or protection from enforcement.

## Install

1. Install **Proton 11.0 (ARM64)** through Steam. The supported build is `1791559733 proton-11.0-2e-arm64`; other component hashes are rejected.
2. Launch ESO through Steam once to initialize its prefix and prerequisites, then close it.
3. Extract the overlay download, enter its `eso-arm64ec-wine-fix` directory, and run:

```bash
python3 scripts/verify.py
python3 scripts/install.py
bash scripts/launch-eso.sh
```

The installer creates **Proton-11.0-ESO-Official-Hotpatch-arm64** beside your existing compatibility tools. It preserves the official installed runtime. The launcher clones an existing Steam-initialized ESO prefix into its own compatibility directory, skipping transient sockets and locks. It preserves the source prefix and refreshes the clone's Wine/FEX core DLLs from the selected tool.

Restart Steam to see **Proton 11.0 ESO Hotpatch (official base, ARM64, experimental)**. The controlled tests used the isolated launcher; selecting the tool in Steam with another prefix has not been separately validated. [Paths, overrides, and rollback](docs/INSTALL.md).

## Is the DLL build method included?

**Yes: the exact post-link transformation is included. Wine was not recompiled.**

- `scripts/reproduce-kernel32-hotpatch.py`: version-checked transformation, separate output only.
- `patches/kernel32-hotpatch-thunks.json`: original and replacement bytes for every slot.
- `bin/kernel32-eso-hotpatch.dll`: the tested precompiled output.
- `evidence/official-source-pins.json` and `source-manifest.json`: exact Valve source revisions and source archive hashes.

```bash
python3 scripts/reproduce-kernel32-hotpatch.py /path/to/original/kernel32.dll /path/to/new/kernel32.dll
```

The script reproduces the shipped DLL byte-for-byte. There is **not yet a source-level Wine/linker patch that emits this layout during compilation**, and independently rebuilding Valve's baseline byte-for-byte has not been demonstrated. [Method and sources](docs/BUILD.md).

## Documentation

[Findings](docs/FINDINGS.md) · [Validation](docs/VALIDATION.md) · [Installation](docs/INSTALL.md) · [Sources and licenses](docs/SOURCES-AND-LICENSES.md) · [Privacy](docs/PRIVACY.md)

This idea may apply to other ARM64EC builds, but the current binary patch and compiled DLL support only the exact tested baseline. Do not copy the DLL into arbitrary Proton or Windows installations.

Wine, Valve Proton, FEX, LLVM and dependency authors retain their licenses and credit. The compiled Wine DLL retains Wine's LGPL terms. New helpers and documentation have the scoped [MIT license](LICENSE). This is not an official Valve, Wine, FEX, or ESO release.
