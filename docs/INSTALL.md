# Install the recommended BNet-based runtime

Requirements: Linux ARM64, Steam, ESO, SteamLinuxRuntime_4-arm64, and the Steam FEX rootfs. The complete archive includes GE-Proton11-7, BNet1's matching Wine/FEX components, and both ESO corrections.

1. Download `GE-Proton11-7-ESO-BNet-arm64.tar.gz` and `SHA256SUMS` from [v0.4.1](https://github.com/dxu16/eso-arm64ec-wine-fix/releases/tag/v0.4.1).
2. Verify the archive: `sha256sum -c SHA256SUMS --ignore-missing`.
3. With Steam fully closed, preserve an existing tool folder outside `compatibilitytools.d`, then extract the archive into a fresh destination under `~/.local/share/Steam/compatibilitytools.d/`. The archive contains one `GE-Proton11-7-ESO-BNet-arm64` tool folder; do not merge installations.
4. Restart Steam and choose **GE-Proton11-7 ESO BNet (ARM64, experimental)** under ESO > Properties > Compatibility.
5. For a clean prefix, close ESO and move or rename its `steamapps/compatdata/306130` folder so that the exact `306130` path is absent, then launch normally. Preserve the backup until the new setup works. Steam's Developer > Delete Proton Files option did not clear this path in our Armada test.

No Python installer, compiler, or separate original BNet/GE download is required. Steam still supplies external runtime dependencies and ESO's first-run prerequisites. First launch can take longer while Proton creates its template prefix. Keep your shader caches and known-working FEX settings for comparison.

Do not extract over a running tool. Existing comparison installations with kernel32 SHA256 `5b9c2d116f93a307e7b69c31544e52b7a5081fa7caa384020b1c09f948664d5b` and ntdll SHA256 `5da92139e0e34111acf952b4d7ba590da09d34fdb9e99b68086c6081bcda16ac` already have these same runtime corrections. The v0.4.0 package changes their registration and documentation, not these binaries.

Rollback: close ESO and select your previous compatibility tool. The installer-free archive leaves other tools available. Preserve or back up an existing Wine prefix before deliberately changing or deleting it; this package does not include a game prefix.

The old `scripts/install.py` is a legacy Valve-only overlay installer. Use [legacy instructions](legacy-valve/INSTALL.md) only when intentionally choosing v0.3.0.

## Fresh-prefix launcher failure in v0.4.0

On 30 October 2026, a new prefix reproduced a Bethesda launcher stack overflow on the original test handheld. Ten bundled fonts, including Arial and Tahoma, were present on disk but absent from the prefix's font registry. The established prefix already had these registrations. Official Proton 11.0-2e ARM64 also supplied them in a clean-prefix control. This is separate from ESO's five-minute self-exit.

For an affected existing prefix, close ESO and its Wine processes, then run the helper from this source checkout:

```sh
python3 bnet/repair-launcher-fonts.py "$HOME/.local/share/Steam/steamapps/compatdata/306130"
```

Adjust the path if ESO's prefix is in another Steam library. The helper adds only missing registrations for ten existing font files, preserves existing values, and saves a byte-for-byte `system.reg.before-eso-font-repair-*` backup beside `system.reg`. It refuses active prefixes and missing fonts. It does not download fonts or replace Wine/FEX DLLs. Running it again makes no further changes.

v0.4.1 makes the fonts visible before Wine generates its template, so new prefixes receive the registrations automatically. Existing affected prefixes still need the helper above or a clean prefix. The reproduction recipe is in [BUILD.md](BUILD.md). Other-device validation remains outstanding.
