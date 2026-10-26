# Install the recommended BNet-based runtime

Requirements: Linux ARM64, Steam, ESO, SteamLinuxRuntime_4-arm64, and the Steam FEX rootfs. The complete archive includes GE-Proton11-7, BNet1's matching Wine/FEX components, and both ESO corrections.

1. Download `GE-Proton11-7-ESO-BNet-arm64.tar.gz` and `SHA256SUMS` from [v0.4.0](https://github.com/dxu16/eso-arm64ec-wine-fix/releases/tag/v0.4.0).
2. Verify the archive: `sha256sum -c SHA256SUMS --ignore-missing`.
3. Extract into `~/.local/share/Steam/compatibilitytools.d/` using a fresh destination. The archive contains one `GE-Proton11-7-ESO-BNet-arm64` tool folder.
4. Restart Steam and choose **GE-Proton11-7 ESO BNet (ARM64, experimental)** under ESO > Properties > Compatibility.

No Python installer, compiler, or separate original BNet/GE download is required. Steam still supplies external runtime dependencies and ESO's first-run prerequisites. First launch can take longer while Proton creates its template prefix. Keep your shader caches and known-working FEX settings for comparison.

Do not extract over a running tool. Existing comparison installations with kernel32 SHA256 `5b9c2d116f93a307e7b69c31544e52b7a5081fa7caa384020b1c09f948664d5b` and ntdll SHA256 `5da92139e0e34111acf952b4d7ba590da09d34fdb9e99b68086c6081bcda16ac` already have these same runtime corrections. The v0.4.0 package changes their registration and documentation, not these binaries.

Rollback: close ESO and select your previous compatibility tool. The installer-free archive leaves other tools available. Preserve or back up an existing Wine prefix before deliberately changing or deleting it; this package does not include a game prefix.

The old `scripts/install.py` is a legacy Valve-only overlay installer. Use [legacy instructions](legacy-valve/INSTALL.md) only when intentionally choosing v0.3.0.
