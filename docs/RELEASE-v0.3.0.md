# ESO ARM64EC Wine fix v0.3.0 â€” performance correction

This is the default recommended experimental package for the exact Valve Proton 11.0-2e ARM64 baseline. It includes the existing kernel32 startup fix and the new ntdll ARM64EC call-checker correction. FEX, kernelbase, WOW64, and GPU components remain unchanged.

The kernel32-only fix introduced a native-call emulation detour. A standalone CRT allocation/free benchmark measured about 218 ns stock, 551 ns kernel32-only, and 222 ns with both fixes. These are not ESO FPS or loading-time measurements. The user confirmed significantly improved performance through Steam during play.

The isolated title test survived seven minutes with zero API-entry reports under Armada Default settings and an unchanged shader cache. It included a brief suspend and did not measure load time. Long-session stability and account safety remain unestablished.

Download the performance overlay, verify its checksums, extract it, and run `python3 scripts/verify.py` followed by `python3 scripts/install.py`. Restart Steam and select **Proton 11.0 ESO Performance Hotpatch (ARM64, experimental)** in ESO's Compatibility settings. Existing tools are preserved as fallbacks; no launch script is required.

Both precompiled DLLs, exact post-link reproduction scripts, complete change manifests, and an equivalent Wine source patch are included. Wine was not recompiled. The equivalent source patch applies to the pinned Wine source but was not compiled into these binaries. The full pinned Wine source and Proton build recipes are supplied as source archives. Wine binaries and the Wine source patch retain their LGPL terms.

## Ready-to-use full tool

A full ready-to-extract `Proton-11.0-ESO-Performance-Hotpatch-arm64.tar.gz` is also available. Extract its tool folder into `~/.local/share/Steam/compatibilitytools.d/`, restart Steam, and select the tool for ESO. No manual installer or separate base-Proton installation is required. Steam’s Linux ARM64 runtime and FEX rootfs remain prerequisites. The small overlay remains available.

The full archive excludes generated prefixes, caches, logs and device data, and includes canonical metadata and internal file hashes. Matching component source archives and patch sources are supplied in the separate runtime-sources archive. The DLLs are identical in both downloads.
