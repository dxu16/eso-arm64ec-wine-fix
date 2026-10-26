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
