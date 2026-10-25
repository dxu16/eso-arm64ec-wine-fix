# Sources, notices, and distribution

The distributed binaries are modified Wine kernel32 and ntdll from official Valve Proton 11.0-2e ARM64. They retain Wine's LGPL-2.1-or-later terms. The root MIT license covers only new helper scripts and documentation, not third-party binaries, notices, or sources.

Two downloads are available. The small overlay installer clones the user's Steam-installed runtime. The ready-to-use archive includes the full official-base compatibility tool, additional component notices, and access to its separate runtime source bundle. FEX and the other runtime libraries remain unchanged. Wine, Valve, FEX, LLVM, and dependency authors retain their respective rights and attribution.

The release includes:

- Exact full Valve Wine source at e60892cc2398b0a83c332a2078c7b85e47bdb42b.
- Proton root source/build recipes at bc896217ffcd67f892f952b010f898fe7bd0f0a1.
- Both additional binary-transformation recipes and manifests, a native helper assembly reference, and an equivalent Wine source patch.
- The Wine source patch retains Wine's LGPL terms; it is not relicensed under the root MIT license.
- Relevant Wine and compiler-runtime notices under LICENSES/.

The original Proton root archive does not recursively include its submodules. The expanded runtime source bundle supplies the pinned component archives and nested dependencies, as well as the matching Wine Mono and Gecko source releases; test-only datasets are omitted. The overlay can still obtain unchanged runtime binaries from Steam. The full source of the modified Wine component is supplied separately. SOURCE archive hashes are in source-manifest.json and release-manifest.json. Independently rebuilding Valve's baseline byte-for-byte is not claimed.

BNet and its credited GameNative authors helped establish the original diagnosis. Those earlier files and their notices remain in scrubbed Git history. This current official-base overlay does not contain BNet or GE-Proton runtime components. This project is not an official release or endorsement from Valve, Wine, FEX, or ZeniMax.

The full runtime component source index is `runtime-source-manifest.json`. The binary archive retains the official LICENSE, LICENSE.OFL and PATENTS.AV1 files, and adds component notices under `eso-hotpatch/LICENSES/runtime/`. SteamLinuxRuntime_4-arm64 and the Steam FEX rootfs remain external dependencies and are not redistributed. The documented upstream mutable branch and whole-baseline rebuild limits also apply to this source bundle.
