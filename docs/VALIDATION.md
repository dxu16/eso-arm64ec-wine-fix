# Current performance fix (v0.3.0)

The default now patches both kernel32 and ntdll. The original kernel32-only tests below are historical controls.

The standalone allocation/free benchmark measured medians of 218.205 ns stock, 550.910 ns kernel32-only, and 222.110 ns with the ntdll correction. This does not measure ESO FPS or load time.

The performance candidate survived a 420-second timeout (422.021 wall seconds; 415.893 trace seconds after game load), with zero API-entry reports. It used a copy of the existing Steam prefix and unchanged shader cache, the Armada wrapper, and the existing Default FEX profile. A brief suspend was reported; this run is not a loading-time measurement. Native patch bytes were verified in the running process. SEH tracing was disabled, so shutdown-thread absence was not measured in this test.

The user then selected the tool through Steam and reported significantly improved performance during play. No numeric FPS/loading measurements or long-session duration were supplied. This is user confirmation, not an independently instrumented gameplay benchmark. Evidence is in the performance JSON files under evidence/.

# Earlier kernel32-only validation

# Validation

Tests performed 24 October 2026 on an Armada OS Linux aarch64 handheld, kernel 7.2.6. Base: Valve `1791559733 proton-11.0-2e-arm64`. Source revision and component hashes are in `evidence/official-source-pins.json` and `evidence/validation-results.json`.

| Case | Outcome |
| --- | --- |
| Stock official runtime, fresh Wine prefix | Shutdown thread; exit 0x1101 after 305.807 game seconds; not the decisive control |
| Stock official runtime, cloned Steam-initialized prefix | 28 API-entry reports; shutdown thread; exit 0x1100 after 305.376 game seconds |
| Official runtime + kernel32 correction, identically initialized prefix | Zero API-entry reports; no observed shutdown thread; animated title screen; survived 420-second timeout |
| Actual packaged installer and dependency-preserving launcher | Zero API-entry reports; survived a second 420-second timeout |

The successful wrappers returned **124**, from the explicit timeout. Filter wall times were about 422 seconds including wrapper overhead; this is not a claim that the title screen was shown for that entire interval. The first patched run had SEH tracing and an empty shutdown-thread log. The installer/launcher run had process/module tracing without SEH tracing, so shutdown-thread absence was not measured by that method in the second run.

The fresh and Steam-initialized prefixes differed beyond just their runtime. The distinct 0x1101 result was not isolated to a particular missing redistributable. Both decisive A/B runs copied the same existing ESO Steam prefix. No manual changes were made to that original prefix.

Loaded prefix hashes confirmed stock Valve FEX, ntdll, kernelbase, and the WOW64 translator. A baseline prefix audit found 504 matching official Wine DLLs and no differing Wine-builtin DLL among the inspected ARM64 system DLLs. The candidate differs only in kernel32's entry-layout correction; custom tool registration and helper files do not change FEX or Wine implementations.

Conservative options:

```text
FEX_SMC_CHECKS=full
FEX_TSOENABLED=1
FEX_VECTORTSOENABLED=1
FEX_MEMCPYSETTSOENABLED=1
FEX_HALFBARRIERTSOENABLED=0
FEX_X87REDUCEDPRECISION=0
FEX_MULTIBLOCK=0
```

**No login or gameplay was tested.** Long-session stability, account enforcement, other platforms/builds, performance, and minimum required FEX settings remain unknown. Modified DLL bytes can be detected by other checks. Passing this startup test does not establish approval or account safety.

## Earlier result

The BNet-based proof also survived two seven-minute controls. The new official-base comparison shows that BNet's additional Wine/FEX changes are not required for the measured self-exit. Scrubbed BNet source history remains at the `v0.1.0-experimental` Git tag; its release has been removed.

## Standalone benchmark source

`scripts/benchmark-api.c` contains the x64 Windows benchmark (no ESO code). Build with `zig cc -target x86_64-windows-gnu -O2 scripts/benchmark-api.c -o api-bench.exe`, and pass a writable Windows result-file path when running it under each isolated runtime. It performs one million 128-byte allocation/free pairs and also reports direct API timings. Compare warmed, repeated runs; it is not a game benchmark.

## Ready-to-use archive validation

The runtime archive passed its internal file-hash, canonical-metadata and symlink/path checks. A fresh extraction without any generated default prefix successfully created that prefix on first use and completed the standalone benchmark (221.56 ns per allocation/free pair). The extracted tool then survived a 420-second ESO timeout, with zero API-entry reports observed beyond the old five-minute exit point. It used an isolated Steam-initialized prefix and Armada Default settings, without SEH tracing. Final notice/source-metadata additions were verified not to change runtime file contents or symlink targets. All 74 component source archive contents were independently checked against their recorded hashes. See evidence/ready-runtime-validation.json.
