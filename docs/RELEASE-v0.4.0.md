# ESO BNet / GE-Proton 11 ARM64 v0.4.0

**BNet is now the recommended default.** This full runtime combines [mrdidit's original BNet1](https://github.com/mrdidit/bnet-arm/releases/tag/BNet1), on GE-Proton11-7 ARM64, with the ESO kernel32 startup correction and matching ntdll native-call performance correction.

## Why the base changed

The user compared vanilla GE and BNet with the same ESO corrections and reported less stuttering with BNet. They had also observed intermittent spikes with the Valve-based runtime, including while idle and at the login screen. This is a practical user-reported improvement on one device, not an instrumented frame-time benchmark, a universal stutter fix, or proof that a particular BNet patch is responsible.

The BNet FEX/UnixLib components are kept together, and GE's graphics components are retained. Neither the game executable nor global FEX settings are changed by the package. The previous [Valve-based v0.3.0](https://github.com/dxu16/eso-arm64ec-wine-fix/releases/tag/v0.3.0-experimental) remains available as a fallback.

## Download and use

Download **GE-Proton11-7-ESO-BNet-arm64.tar.gz** and verify it against **SHA256SUMS**. Extract its single folder into `~/.local/share/Steam/compatibilitytools.d/`, restart Steam, and select **GE-Proton11-7 ESO BNet (ARM64, experimental)** for ESO. No compiler, Python installer, or separate GE/BNet installation is needed. Steam's Linux ARM64 runtime and FEX rootfs remain required.

Existing BNet ESO comparison installations with the documented identical DLL hashes already have these code corrections; they do not require reinstalling to gain an additional performance patch.

## Validation

- Both comparison candidates survived separate 420-second ESO startup tests and reached the title screen; timeout exit 124 was intentional.
- BNet's standalone allocation/free result was 195.92 ns per pair; vanilla GE measured 195.47 ns. These are single-run microbenchmarks, not ESO FPS or stutter measurements.
- The native helper matched independent assembly and was verified in the running game. On-disk DLL hashes matched the intended tools.
- Exact post-link reconstruction/reproduction and rejection checks passed. Wine was not recompiled.
- The full release archive is checked for every indexed file, safe paths/symlinks, canonical metadata, the six core Wine/FEX hashes, and exclusion of generated prefixes/caches.

The package remains experimental; long-session stability and performance on other setups remain unmeasured. No additional device gameplay testing was run for publication after the user's request to stop testing.

## Upstream credit and sources

Please see and credit **[the original BNet repository](https://github.com/mrdidit/bnet-arm)**. BNet is maintained by **mrdidit**. Its original Blizzard compatibility fixes are by **Dmage22**, integrated through **GameNative**, with contributions from **tarikbc** and **Utkarsh Dalal**. **GloriousEggroll**, Wine, FEX, LLVM and dependency authors retain their respective credits and licenses. This release adds ESO-specific Wine entry/dispatch corrections; it does not claim authorship of BNet's patches.

All runtime notices are preserved. The three original BNet/GE corresponding-source archives, the ESO patch-source archive, `source-manifest.json`, `release-manifest.json`, and checksums accompany the binary. Wine-derived modifications remain under LGPL terms; other components retain their licenses.
