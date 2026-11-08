# v0.4.2 — Isolate Steam graphics probes

This maintenance release retains the v0.4.1 font initialization fix and the existing ESO startup and native-call corrections. Steam's automatic graphics probes now use separate prefixes for each runtime, probe executable, and DirectX mode. This prevents the shared compatdata/0 prefix from linking different Wine builds during probe initialization.

## Installation

Close Steam and applications using the existing runtime. Verify the archive with the attached SHA256SUMS, then extract the complete tool into a fresh GE-Proton11-7-ESO-BNet-arm64 directory under ~/.local/share/Steam/compatibilitytools.d. Preserve an existing tool until its replacement works. Restart Steam and retain the current ESO compatibility selection and launch options. Fresh prefixes still follow the official-Proton-first sequence in [INSTALL.md](INSTALL.md).

## Changes and validation

- Added a runtime entry-point wrapper that isolates only Steam graphics probes and forwards ordinary launches to Proton.
- Added child-lifetime locks, signal forwarding, and a checksum-aware installer for existing tools.
- Added wrapper and installer regression tests to the existing verification workflow.
- The packager requires the exact published v0.4.1 archive and retains the pinned Wine/FEX binaries and ESO DLL corrections.

Mechanism, tests, cache cleanup, and local installation are documented in [GRAPHICS-PROBES.md](GRAPHICS-PROBES.md). The wrapper and all packaging/test sources are included in the complete runtime and the additional source bundle.

The release includes the complete runtime, ESO-BNet-v0.4.2-patch-sources.tar.gz, the original three BNet/GE corresponding-source archives, source and release manifests, and SHA256SUMS. Original credits and licenses remain in the package.
