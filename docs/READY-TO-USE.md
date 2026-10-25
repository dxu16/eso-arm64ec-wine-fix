# Ready-to-use compatibility tool

Download `Proton-11.0-ESO-Performance-Hotpatch-arm64.tar.gz` from v0.3.0-experimental. Verify its SHA256 against the release's SHA256SUMS, then extract its single tool folder into `~/.local/share/Steam/compatibilitytools.d/`. Restart Steam and select **Proton 11.0 ESO Performance Hotpatch (ARM64, experimental)** for ESO.

No compiler or manual `install.py` invocation is needed. The archive contains the full official Proton 11.0-2e ARM64 compatibility tool with both DLL fixes applied. A separate installation of the original Proton tool is not required. Steam, ESO, SteamLinuxRuntime_4-arm64 and Steam's FEX rootfs remain prerequisites. The original tool manifest's `require_tool_appid` is preserved.

Use a fresh destination. Do not extract over a running tool or over immutable-protected DLLs. Existing installations with these same DLL hashes already have the fix; reinstalling them is unnecessary. The small overlay installer remains available as an alternative.

## What is excluded?

The package excludes generated default prefixes, registries, logs, Python bytecode, locks, and device-local settings. Archive ownership and timestamps are canonicalized. Symlinks stay inside the tool. It contains no ESO executable or game data and no personal Steam/Wine prefix.

Proton recreates its default prefix on first launch. The package filters the omitted prefix entries from SteamPipe's directory metadata so they cannot recreate an empty prefix prematurely. The first launch can consequently take longer than later launches. The launcher code and runtime libraries are otherwise retained; only kernel32 and ntdll have the documented binary corrections, alongside custom tool registration and packaging metadata.

## Integrity and source material

`python3 scripts/verify-runtime.py /path/to/the/archive.tar.gz` verifies internal file hashes, paths, symlinks, owner metadata, both patched DLL hashes, and prefix exclusions without extracting or executing the archive. `scripts/package-runtime.py` is the packaging recipe for a prepared tool with the matching component notices.

The separate `Proton-11.0-ESO-Performance-Hotpatch-arm64-runtime-sources.tar.gz` contains component source archives, build recipes, the exact post-link patch sources, and a component index. It is not needed to run the tool. `runtime-source-manifest.json` records upstream locations and hashes; `scripts/fetch-runtime-sources.py` can retrieve those component archives individually. The source bundle preserves upstream notices, and the binary includes additional notices under `eso-hotpatch/LICENSES/runtime/`.

The source index records the mutable upstream Piper dependency branch and its resolved revision. Independently rebuilding Valve's whole baseline byte-for-byte has not been demonstrated. General-purpose build SDK/compiler packages and Steam's external Linux runtime/rootfs are not bundled here.

Optional immutable protection for the two patched DLLs is described in INSTALL.md. Apply it only after successful first launch; clear it before intentional updates or removal.
