# BNet runtime validation and observed stutter

On 25 October 2026, vanilla GE-Proton11-7 ARM64 and BNet1 were each tested with the matching ESO kernel32 and ntdll corrections on the same KONKR Pocket FIT Elite running Armada.

| Check | Vanilla GE + ESO fixes | BNet + ESO fixes |
| --- | --- | --- |
| Standalone 128-byte allocation/free pair | 195.47 ns | 195.92 ns |
| ESO startup timeout | Survived 420 seconds | Survived 420 seconds |
| Title screen capture | Confirmed | Confirmed |
| Intended prefix DLL hashes | Matched | Matched |
| Native helper bytes in running ESO | Matched | Matched |

The timeout wrappers returned 124 intentionally. These were isolated copies of a Steam-initialized prefix using the Armada launch wrapper and existing global FEX profile. Verbose Wine tracing was disabled. The allocation figures are single-run microbenchmarks, not gameplay frame times or statistically established performance differences.

The user subsequently reported that the BNet variant reduced stuttering relative to vanilla GE and the earlier Valve-based fix, and requested BNet as the default. No frame-time recordings or numerical stutter counts were supplied. This supports the practical recommendation for that setup; it does not identify an individual BNet patch as the cause or establish the same benefit elsewhere.

Read-only runtime checks verified the ntdll helper and branch. Of 796 corrected kernel32 slots, 788 retained their exact patched bytes after loading; eight were rewritten at runtime in both variants. The writer of those entries was not identified. On-disk hashes of the complete intended DLLs were separately verified. This observation is preserved rather than claiming all entries stay unchanged in memory.

Independent assembly matched the generated helper, import/export tables were preserved, and exact reconstruction/reproduction and rejection checks passed. Both source variants accepted the equivalent source patch; the source patch was not compiled. The packaged BNet archive uses the tested BNet DLL hashes and is checked independently for every indexed file, path, symlink and core component.

Device game/benchmark testing was stopped at the user's request after the BNet startup test; no further such testing is part of this release work. Long sessions and other hardware remain unmeasured. Public records are in `evidence/bnet-validation.json` and `evidence/bnet-user-confirmation.json`.

Earlier Valve results are retained in [legacy validation](legacy-valve/VALIDATION.md).

## Fresh-prefix font initialization investigation, 30 October 2026

A checksum-verified extraction of public v0.4.0, a new game prefix and a new ESO shader cache reproduced an early Bethesda launcher failure on the same Pocket FIT Elite. Launch options were cleared; Armada automatically restored its standard `armada-game-launch %command%` wrapper. Game files and global FEX settings were retained. A second launch also failed.

An isolated diagnostic clone recorded `EXCEPTION_STACK_OVERFLOW` in the 32-bit launcher with WoW64/FEX frames. The same runtime opened a usable launcher with a clone of the established prefix. Registry bisection isolated `HKLM\Software\Microsoft\Windows NT\CurrentVersion\Fonts`. Its ten missing registrations referenced font files already present in the fresh prefix; adding only those entries removed the observed stack overflow. No Wine/FEX binaries or game executable were changed.

The automatic candidate exposes the bundled fonts before `wineboot` creates its template registry. Testing with both a fresh extraction and an empty game prefix generated the entries automatically. A subsequent Steam test with a fresh template, game prefix and shader cache reached the fully rendered launcher with PLAY available. The user then confirmed that the fresh fixed setup worked in-game. Session duration was not specified, so this does not independently establish five-minute survival or long-session stability.

Official Proton 11.0-2e ARM64 was also tested with an empty control prefix and supplied the missing font registrations. Its trace did not show the BNet control's stack overflow. The Steam control displayed its launcher loading screen; this is not recorded as successful gameplay validation. Intermittent launcher startup failure remains distinct from the reproducible missing-font failure.

The repair helper passed checks for byte-for-byte backup preservation, idempotence, missing-font refusal, duplicate-section refusal and active-prefix refusal. The candidate archive passed independent per-file, symlink and six-component verification. The font-initialization change was subsequently published in v0.4.1.

After the user invoked Steam's Developer > Delete Proton Files option, inspection still found the active prefix's registry, runtime version marker and settings from the tested session. No intervening fresh rebuild was evident. The active prefix was then moved aside manually, its absence verified, and ESO launched through Steam with the fixed runtime. Steam recreated the prefix with the font registrations and ran first-time prerequisites; the user confirmed that this first launch succeeded. The shader cache was retained for this repeat, isolating a prefix-only reset.

The official-Proton-first sequence was subsequently tested on the same handheld: official Proton initialized a fresh prefix and reached the launcher with PLAY available, then the same prefix was switched to the original patched v0.4.0 runtime. The user confirmed it worked. A later Odin 3 tester report says official-runtime initialization is still needed with v0.4.1. The remaining direct-start failure on that device has not been diagnosed; fresh setups are therefore instructed to use official Proton first, then retain that prefix when switching to the patched runtime.
