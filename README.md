# ESO on official Proton 11 ARM64

An experimental Wine compatibility and performance fix for ESO on **Valve Proton 11.0-2e ARM64**. The default package includes both the kernel32 startup fix and the ntdll performance correction.

**[Download the prebuilt compatibility tool (~582 MB)](https://github.com/dxu16/eso-arm64ec-wine-fix/releases/download/v0.3.0-experimental/Proton-11.0-ESO-Performance-Hotpatch-arm64.tar.gz)** | [Small overlay and installer (~1 MB)](https://github.com/dxu16/eso-arm64ec-wine-fix/releases/download/v0.3.0-experimental/Proton-11.0-ESO-Performance-Hotpatch-arm64-overlay.tar.gz) | [Checksums and sources](https://github.com/dxu16/eso-arm64ec-wine-fix/releases/tag/v0.3.0-experimental)

The ready-to-use archive includes the full official-base compatibility tool with both DLL fixes applied. Extract it into Steam's compatibility-tools folder and select it. No compiler, manual installer command, or separate base-Proton installation is needed. Steam's ARM64 Linux runtime and FEX rootfs remain prerequisites, as for official ARM64 Proton.

The smaller overlay remains available for users who already have the exact official Proton baseline installed.

## What changed?

- **kernel32.dll:** corrects 796 imported-function entry thunks that ESO mistakes for hooks, preventing the repeatable `0x1100` self-exit after about 305 seconds.
- **ntdll.dll:** teaches Wine's ARM64EC call checker to recognize that entry prolog. Native callers keep the fast import-call path rather than detouring through x64 emulation.

**FEX, kernelbase, the WOW64 translator, and GPU components remain Valve's originals.** ESO's executable and its checks are unchanged. The ntdll correction changes native call-checker code and extends its ARM64EC code range; the kernel32 transformation preserves its native code and metadata.

## Results and limits

| Test | Result |
| --- | --- |
| Stock official runtime | 28 API-entry reports; `0x1100` at about 305 seconds |
| Kernel32-only fix | Startup exit resolved, but introduced allocation/free overhead |
| Both DLL fixes, Armada Default profile | Zero API-entry reports; survived the seven-minute title-screen test |
| User's normal Steam launch and play comparison | User reports significantly improved performance |

A standalone CRT allocation/free benchmark measured **218 ns stock, 551 ns with the kernel32-only fix, and 222 ns with both fixes**, per pair. This is not an ESO FPS or load-time measurement. The user did not supply measured FPS or loading times. The controlled title test included a brief device suspend and was not used to measure loading time.

**Long-session stability, other builds, and account-safety risk remain unestablished.** Successful tests do not establish approval or protection from enforcement. [Validation details](docs/VALIDATION.md).

## Ready-to-use installation

For a fresh destination, extract the full archive:

```bash
mkdir -p ~/.local/share/Steam/compatibilitytools.d
tar -xzf Proton-11.0-ESO-Performance-Hotpatch-arm64.tar.gz -C ~/.local/share/Steam/compatibilitytools.d
```

Restart Steam. In ESO's **Properties > Compatibility**, force **Proton 11.0 ESO Performance Hotpatch (ARM64, experimental)** and launch normally. Allow Steam's first-run prerequisites to finish. The first launch creates its private default prefix and may take longer.

If that tool folder already exists, keep it or move it aside first; do not extract over a running or immutable-protected tool. The full archive and overlay contain the same patched DLLs. [Detailed installation](docs/READY-TO-USE.md).

## Alternative: overlay installer

1. Install **Proton 11.0 (ARM64)** through Steam. The supported build is `1791559733 proton-11.0-2e-arm64`; the installer rejects other component hashes.
2. Launch ESO through Steam once to initialize its prefix and prerequisites, then close it.
3. Extract the overlay download, enter its `eso-arm64ec-wine-fix` directory, and run:

```bash
python3 scripts/verify.py
python3 scripts/install.py
```

4. Restart Steam. In ESO's **Properties > Compatibility**, enable **Force the use of a specific Steam Play compatibility tool** and select **Proton 11.0 ESO Performance Hotpatch (ARM64, experimental)**.
5. Launch normally through Steam. No launch script is required.

The default destination is `~/.local/share/Steam/compatibilitytools.d/Proton-11.0-ESO-Performance-Hotpatch-arm64`. The original Valve runtime is preserved. Existing kernel32-only tools are left available as fallbacks; switch ESO to the new tool explicitly. [Paths, protection, and rollback](docs/INSTALL.md).

## Optional developer launch script

```bash
bash scripts/launch-eso.sh
```

This diagnostic helper clones the Steam-initialized prefix, refreshes five core DLLs, checks both patched DLL hashes, and launches `eso64.exe` directly with conservative FEX settings. Normal Steam launching is the default; the helper is for troubleshooting and reproducing earlier controlled tests.

## Are the DLL build methods included?

**Yes. Both shipped DLLs are reproduced by exact post-link transformations; Wine was not recompiled.**

```bash
python3 scripts/reproduce-kernel32-hotpatch.py original-kernel32.dll new-kernel32.dll
python3 scripts/reproduce-ntdll-performance.py original-ntdll.dll new-ntdll.dll
```

The repository includes both compiled DLLs, complete binary change manifests, the native helper assembly reference, and an equivalent Wine source-level call-checker patch. The source-level patch applies to the pinned Wine source but was not compiled to produce the shipped DLL. A source-level kernel32/linker change is not included. [Reproduction and sources](docs/BUILD.md).

## Documentation

[Findings](docs/FINDINGS.md) | [Validation](docs/VALIDATION.md) | [Installation](docs/INSTALL.md) | [Sources and licenses](docs/SOURCES-AND-LICENSES.md) | [Privacy](docs/PRIVACY.md)

Only the exact tested baseline is supported. Do not copy these DLLs into arbitrary Proton or Windows installations.

Wine, Valve Proton, FEX, LLVM, and dependency authors retain their licenses and credit. The Wine binaries and Wine source patch retain Wine's LGPL terms. New helper scripts and documentation have the scoped [MIT license](LICENSE). This is not an official Valve, Wine, FEX, or ESO release.
