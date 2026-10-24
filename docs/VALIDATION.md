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
