# ESO on BNet / GE-Proton 11 ARM64

The recommended runtime is **GE-Proton11-7 ESO BNet (ARM64, experimental)**: [BNet1](https://github.com/mrdidit/bnet-arm) plus the ESO startup and native-call performance corrections, with the v0.4.1 font-initialization fix for fresh prefixes.

**[Download the complete font-fixed runtime](https://github.com/dxu16/eso-arm64ec-wine-fix/releases/download/v0.4.1/GE-Proton11-7-ESO-BNet-arm64.tar.gz)** | [v0.4.1 release, checksums and sources](https://github.com/dxu16/eso-arm64ec-wine-fix/releases/tag/v0.4.1) | [Release notes](docs/RELEASE-v0.4.1.md)

The previously published [v0.4.0 release](https://github.com/dxu16/eso-arm64ec-wine-fix/releases/tag/v0.4.0) does not include the fresh-prefix font fix.

Extract its tool folder into `~/.local/share/Steam/compatibilitytools.d/`, restart Steam, then select **GE-Proton11-7 ESO BNet (ARM64, experimental)** in ESO's Compatibility settings. No compiler, installer, separate BNet installation, or separate GE installation is needed. Steam's Linux ARM64 runtime and FEX rootfs remain prerequisites. [Installation and rollback](docs/INSTALL.md).

**For a fresh prefix, initialize it with official Proton before switching to the patched runtime, including with v0.4.1.** A tester reports that the latest fix still requires this sequence on their Odin 3:

1. Close ESO and fully exit Steam. Back up the existing `steamapps/compatdata/306130` folder, then move or rename it so that the exact `306130` path is absent. Use the Steam library containing ESO.
2. Start Steam and select the official **Proton 11.0-2e ARM64** runtime for ESO (the version used in our control test).
3. Launch ESO and allow first-time prerequisites to finish. Wait until the launcher opens with **PLAY** available, then close the launcher and wait for Steam to show the game has stopped. Starting the game under official Proton is unnecessary; it may still encounter the original five-minute exit.
4. Switch ESO's Compatibility setting to **GE-Proton11-7 ESO BNet (ARM64, experimental)** and launch again. **Keep the prefix created by official Proton; do not reset it between runtimes.**

Preserve the old prefix until the new setup works. Steam's **Developer > Delete Proton Files** option did not clear the prefix in our Armada test; verify the `306130` path is absent before the official-runtime first launch. This sequence also worked on the test handheld. An existing prefix with missing font registrations can instead use the included [font-registration repair helper](docs/INSTALL.md#fresh-prefix-launcher-failure-in-v040), but that repair has not been shown to resolve the tester's remaining v0.4.1 failure.

## Disclaimer

This patch modifies Wine runtime DLLs to work around what appears to be a false positive in ESO's anti-tampering mechanism. Although ESO appears to be welcoming toward Linux gaming, there is no guarantee that using this patch will not result in an account ban. Additionally, this patch was made autonomously by GPT 6.1 Sol. Use it at your own risk.

## Why BNet is the default

The user observed intermittent stutters with the Valve-based ESO fix and vanilla GE-Proton11-7 with the same ESO corrections. In their comparison, the BNet variant stuttered less. This is a user-reported result on one handheld, not an instrumented frame-time benchmark or proof identifying one specific BNet patch. It is the reason this release recommends the BNet base.

Both comparison variants passed seven-minute startup checks and produced similar standalone allocation timings. That narrow benchmark does not explain or measure the difference in gameplay stutter. [Validation and limits](docs/VALIDATION.md).

## What this release changes

- Starts with GE-Proton11-7 ARM64 and the original BNet1 Wine/FEX component replacements.
- Adds 796 kernel32 imported-entry prologs to resolve the previously measured ESO five-minute self-exit.
- Adds the matching ntdll ARM64EC call-checker correction so those prologs retain the native import-call path.
- v0.4.1 makes bundled fonts available before Wine initializes a new template, preventing the reproduced fresh-prefix launcher stack overflow on the test handheld. Fresh Steam startup and in-game operation were confirmed there. An Odin 3 tester still needed official Proton to initialize a fresh prefix before switching to v0.4.1; follow the sequence above.

The BNet FEX binaries and GE graphics components are preserved. No FEX profile is forced, and ESO's executable is not modified. Wine was not recompiled: the two ESO DLL changes are reproducible post-link transformations. Exact recipes, manifests, an assembly reference, and corresponding sources accompany the release. [Build details](docs/BUILD.md).

The font-fix tools also live in this repository: [existing-prefix repair](bnet/repair-launcher-fonts.py), [automatic launcher patch](bnet/patch-proton-font-init.py), [complete fixed-runtime packager](bnet/package-font-fixed-runtime.py), and [repair tests](bnet/test_font_repair.py). [Source index and build command](bnet/README.md).

## Upstream credit

This is an ESO-specific derivative of **[mrdidit's original BNet project](https://github.com/mrdidit/bnet-arm)**, using its [BNet1 release](https://github.com/mrdidit/bnet-arm/releases/tag/BNet1). BNet's original Blizzard compatibility fixes are by **Dmage22**, integrated through **GameNative**, with contributions from **tarikbc** and **Utkarsh Dalal**. The GE-Proton base is by **GloriousEggroll**; Wine, FEX, and dependency authors retain their credits and licenses. These upstream changes are not presented as new work by this project. [Sources, attribution and licenses](docs/SOURCES-AND-LICENSES.md).

## Earlier Valve-based package

[v0.3.0-experimental](https://github.com/dxu16/eso-arm64ec-wine-fix/releases/tag/v0.3.0-experimental) remains available as a fallback. The helpers under `scripts/`, the binaries under `bin/`, and the root Valve source indexes preserve its reproduction material; they do not install the recommended BNet tool. Current BNet material lives under `bnet/`. [Legacy Valve instructions](docs/legacy-valve/INSTALL.md).

The runtime remains experimental. Long-session stability and performance on other devices have not been established.
