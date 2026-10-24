# Investigation findings

## Symptom and controls

ESO deterministically called its own termination path with exit code 4352
(`0x1100`), approximately 305 seconds after loading, on the tested Armada
ARM64EC runtime. The game ran on Windows and on native x64 Proton on Steam
Deck. All three installations had the same `eso64.exe` SHA256:

```text
187ed27fe474b5f702c16ed0d405d84c4070f73b055352defb96125ad89fde88
```

The native Windows control remained responsive at the login screen for at
least 413 seconds. The Steam Deck control reached its title screen and
survived a 345-second timeout. No credentials were submitted.

## Cause isolated

The game starts a shutdown thread that waits 300000 ms before taking its
termination path. Its entry traps are at RVAs `0x28b4839` and `0x28b483e` in
this exact ESO version. The working native Deck control did not create it.

A bounded diagnostic FEX logger captured a startup API-validation routine
while it was temporarily decrypted. No decrypted game code is distributed
here. The routine's body starts at RVA `0x28e8915`, and its return trap is at
`0x28e8c22`. It walks 0x38-byte API records referenced by globals at RVAs
`0x3a947d0` and `0x3a947d8`. Its helper at `0x289bd90` classifies entrypoint
patterns including indirect jumps, direct jumps, and push/return sequences.

On the original BNet ARM64EC runtime, 28 registered API records became
reported. They pointed to legitimate kernel32 imported exports beginning
with `FF 25 disp32`: QueryPerformanceCounter, GetLocalTime, GetSystemTime,
VirtualAlloc, GetCurrentDirectoryW, ReadDirectoryChangesW,
SetProcessMitigationPolicy, VirtualProtect, CreateThread, CreateTimerQueue,
CreateTimerQueueTimer, DeleteTimerQueueTimer, GetProcessHeap, HeapFree,
GetLastError, MapViewOfFile, UnmapViewOfFile, OpenProcess, GetComputerNameExW,
QueryFullProcessImageNameW, GetSystemInfo, GetProcessMitigationPolicy,
FlushInstructionCache, ReadProcessMemory, K32GetMappedFileNameW,
K32InitializeProcessForWsWatch, K32GetModuleFileNameExW, and K32GetWsChangesEx.

Native x64 Wine's `tools/winebuild/spec32.c` deliberately prefixes imported
export thunks with an eight-byte hotpatch prolog. Wine's ARM64EC export path
instead uses linker-generated entry thunks and lacks that prolog for these
imported exports. The observed failure is a compatibility mismatch between
this entry layout and ESO's API-hook checks.

## Implemented correction

Within 796 existing aligned 16-byte x64 imported-export slots in kernel32:

```asm
; Before
jmp qword ptr [rip + displacement]
; Ten bytes of existing padding

; After: same entry sequence as native x64 Wine's imported-export path
lea rsp, [rsp + 0]                    ; 48 8d a4 24 00 00 00 00
jmp qword ptr [rip + displacement-8]  ; ff 25 ...
; Two original padding bytes
```

The LEA changes neither RSP nor flags. Adjusting the RIP displacement by -8
preserves the exact original import-slot target. Entry addresses, file size,
export/import tables, hybrid metadata, and native ARM64 code are preserved.
Only 7963 bytes inside the recorded thunk slots differ. The manifest records
every original and replacement sequence. Unknown input versions are rejected.

After this change, the startup registry had zero reported API hooks and the
five-minute timer thread was absent. Two full runs passed seven minutes;
the minimal run used original BNet FEX, ntdll, and kernelbase. This correction
belongs at the Wine/ARM64EC linking boundary, rather than in FEX emulation.

## Earlier experiments and limits

Strict memory ordering, full SMC checks, x87 precision changes, an upstream
x87 FIP correction, private exception-context/RF/DF/x87 bridge corrections,
and a working-set API stub experiment did not eliminate the original exit.
The context experiments identified separate probe differences, but they are
not included in this fix. Replacing imports with standard PE forwarders
caused earlier startup failure and was discarded.

Architecture-reporting differences between native x64 and ARM64EC were
observed, but were not established as the cause. A game-owned ntdll hook was
also observed; it must not be attributed to FEX merely because it is a jump.

The correction is version-specific and currently applied after linking. It
does not establish login/gameplay compatibility, fix all protection schemes,
or establish the minimum FEX settings required for performance. No source
patch has been submitted upstream. The compiled runtime contains no private
FEX context changes or diagnostic logger.
