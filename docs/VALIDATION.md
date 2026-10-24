# Validation

Date: 24 October 2026. Device: KONKR Pocket FIT, Armada OS, Linux aarch64,
kernel 7.2.6. Base compatibility tool: GE-Proton11-7-Bnet1-arm64.

| Configuration | Observation |
| --- | --- |
| Original BNet ARM64EC | Repeated self-exit `0x1100` around 305 seconds |
| Native Windows, same game hash | Responsive at login for at least 413 seconds; closed normally |
| Native x64 Proton 11.0 on Deck | Title screen; survived 345-second timeout |
| Kernel32 correction + earlier context experiments | Title screen; survived 420-second timeout; no shutdown thread |
| Kernel32 correction + original BNet FEX/ntdll/kernelbase | Title screen; survived 420-second timeout |

Both corrected full runs ended with wrapper status **124**, from the explicit
test timeout. Neither logged a game `NtTerminateProcess` call. Stream-filter
wall times were 422.034 and 422.020 seconds; these include wrapper overhead
and are not a claim that the title screen was displayed for the entire time.

The short instrumented startup capture reported zero API-hook records after
the correction. The fully instrumented long run had an empty timer-thread
log and no detected timer TID. SEH tracing was disabled for the minimal run,
so timer absence was not measured by the same trace method in that run.

The working-set API probe retained FALSE/error 120 and untouched buffers.
The architecture/LastError probe retained its original ARM64EC results and
preserved handler/resume LastError values. These are narrow regression
checks, not comprehensive Wine or FEX conformance testing.

Conservative FEX options used for both full controls:

```text
FEX_SMC_CHECKS=full
FEX_TSOENABLED=1
FEX_VECTORTSOENABLED=1
FEX_MEMCPYSETTSOENABLED=1
FEX_HALFBARRIERTSOENABLED=0
FEX_X87REDUCEDPRECISION=0
FEX_MULTIBLOCK=0
```

No login, server connection, gameplay, long-session stability, default-setting
performance, alternate OS, or alternate runtime/game version was verified.
The original installed BNet components retained their original hashes.

Machine-readable records: [`../evidence/`](../evidence/).

## Repository packaging checks

The reproduction and rejection checks passed on Windows and Armada Linux.
Linux disposable-fixture checks verified separate installation, preservation
of baseline components, replacement of the template DLL, rejection of an
existing/nested destination and unsupported baseline, and the installed
embedded verifier. The portable launcher fixture checked prefix preparation,
the conservative environment, arguments, lock cleanup and active-lock
rejection. Shell syntax and the repository's local documentation links were
also checked. These helper tests did not launch ESO and do not extend the
game-validation scope above.
