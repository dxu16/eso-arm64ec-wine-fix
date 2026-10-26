# Why this fixes the measured shutdown

ESO reads the entry bytes of Windows API functions. Wine's kernel32 is a separate file from ESO, but it is loaded into the game's address space and is visible to these checks. Being outside the game executable does not make the library unobservable. [Microsoft DLL documentation](https://learn.microsoft.com/en-us/windows/win32/dlls/about-dynamic-link-libraries).

The startup routine at RVA 0x28e8915 walks 0x38-byte records referenced by RVAs 0x3a947d0/0x3a947d8. Its helper at 0x289bd90 recognizes jump patterns often associated with API hooks. The official runtime produced 28 reported records, including VirtualAlloc, VirtualProtect, QueryPerformanceCounter, GetLastError, CreateThread, and timer APIs. A thread then waited 300000 ms before the measured 0x1100 self-exit.

These are legitimate imported-export thunks. The native x64 Wine export generator in tools/winebuild/spec32.c prefixes such thunks with a hotpatch prolog. The ARM64EC build uses linker-generated thunks without that entry sequence.

```asm
; Before
jmp qword ptr [rip + displacement]
; ten existing padding bytes

; After
lea rsp, [rsp + 0]                    ; 48 8d a4 24 00 00 00 00
jmp qword ptr [rip + displacement-8]  ; ff 25 ...
; two original padding bytes
```

The LEA leaves RSP and flags unchanged. The adjusted displacement addresses the exact original import slot. The patch stays inside existing 16-byte slots and preserves entry addresses, tables, native ARM64 code, and hybrid metadata.

On official Proton 11.0-2e ARM64, 796 replacements produced zero API-entry reports and no observed shutdown thread. The game reached its animated title screen and survived seven minutes. The installed-package launcher repeated the timeout result using a cloned Steam-initialized prefix.

The original thunks are valid code. This is a compatibility correction for a detection heuristic, not proof of an ARM64EC ABI violation. Other integrity checks may still notice the changed bytes. Broader applicability is plausible but untested.

## What was not required

The original kernel32-only control kept Valve's FEX, ntdll, kernelbase, and WOW64 translator unchanged. The current default also corrects ntdll's call checker to preserve fast native import calls; FEX, kernelbase, and WOW64 remain unchanged. Earlier BNet/FEX exception-context and x87 experiments were not needed to resolve this particular self-exit and are not included. Replacing imports with ordinary PE forwarders caused earlier startup failure and was discarded.

## Scope

The measurements apply to ESO executable SHA256 `187ed27fe474b5f702c16ed0d405d84c4070f73b055352defb96125ad89fde88` and the pinned runtime. Controlled measurements do not establish account safety, general anti-tamper compatibility, or correctness of every FEX instruction/context path. No proprietary executable, decrypted game code, or raw process dump is distributed.

## Performance regression and correction

Wine recognizes FF25 import-jump entries in its ARM64EC call checker. The added kernel32 identity LEA prevented that fast recognition for native callers, causing an emulation detour. Recognizing the prolog before the existing import check recovered near-stock CRT allocation/free performance. The user confirmed significantly improved ESO performance through Steam with both DLL corrections. See BUILD.md and VALIDATION.md for exact scope.
