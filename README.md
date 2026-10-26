# ESO on BNet / GE-Proton 11 ARM64

The recommended runtime is now **GE-Proton11-7 ESO BNet (ARM64, experimental)**: [BNet1](https://github.com/mrdidit/bnet-arm) plus the ESO startup and native-call performance corrections.

**[Download the complete runtime](https://github.com/dxu16/eso-arm64ec-wine-fix/releases/download/v0.4.0/GE-Proton11-7-ESO-BNet-arm64.tar.gz)** | [Release, checksums and sources](https://github.com/dxu16/eso-arm64ec-wine-fix/releases/tag/v0.4.0)

Extract its tool folder into `~/.local/share/Steam/compatibilitytools.d/`, restart Steam, then select **GE-Proton11-7 ESO BNet (ARM64, experimental)** in ESO's Compatibility settings. No compiler, installer, separate BNet installation, or separate GE installation is needed. Steam's Linux ARM64 runtime and FEX rootfs remain prerequisites. [Installation and rollback](docs/INSTALL.md).

## Why BNet is the default

The user observed intermittent stutters with the Valve-based ESO fix and vanilla GE-Proton11-7 with the same ESO corrections. In their comparison, the BNet variant stuttered less. This is a user-reported result on one handheld, not an instrumented frame-time benchmark or proof identifying one specific BNet patch. It is the reason this release recommends the BNet base.

Both comparison variants passed seven-minute startup checks and produced similar standalone allocation timings. That narrow benchmark does not explain or measure the difference in gameplay stutter. [Validation and limits](docs/VALIDATION.md).

## What this release changes

- Starts with GE-Proton11-7 ARM64 and the original BNet1 Wine/FEX component replacements.
- Adds 796 kernel32 imported-entry prologs to resolve the previously measured ESO five-minute self-exit.
- Adds the matching ntdll ARM64EC call-checker correction so those prologs retain the native import-call path.

The BNet FEX binaries and GE graphics components are preserved. No FEX profile is forced, and ESO's executable is not modified. Wine was not recompiled: the two ESO DLL changes are reproducible post-link transformations. Exact recipes, manifests, an assembly reference, and corresponding sources accompany the release. [Build details](docs/BUILD.md).

## Upstream credit

This is an ESO-specific derivative of **[mrdidit's original BNet project](https://github.com/mrdidit/bnet-arm)**, using its [BNet1 release](https://github.com/mrdidit/bnet-arm/releases/tag/BNet1). BNet's original Blizzard compatibility fixes are by **Dmage22**, integrated through **GameNative**, with contributions from **tarikbc** and **Utkarsh Dalal**. The GE-Proton base is by **GloriousEggroll**; Wine, FEX, and dependency authors retain their credits and licenses. These upstream changes are not presented as new work by this project. [Sources, attribution and licenses](docs/SOURCES-AND-LICENSES.md).

## Earlier Valve-based package

[v0.3.0-experimental](https://github.com/dxu16/eso-arm64ec-wine-fix/releases/tag/v0.3.0-experimental) remains available as a fallback. The helpers under `scripts/`, the binaries under `bin/`, and the root Valve source indexes preserve its reproduction material; they do not install the recommended BNet tool. Current BNet material lives under `bnet/`. [Legacy Valve instructions](docs/legacy-valve/INSTALL.md).

The runtime remains experimental. Long-session stability and performance on other devices have not been established.
