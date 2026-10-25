# Sources, notices, and distribution

The distributed binaries are modified Wine kernel32 and ntdll from official Valve Proton 11.0-2e ARM64. They retain Wine's LGPL-2.1-or-later terms. The root MIT license covers only new helper scripts and documentation, not third-party binaries, notices, or sources.

This release is an overlay, not a redistributed complete Proton runtime. The installer clones the user's Steam-installed runtime and retains its notices. FEX and the other runtime components remain unchanged. Wine, Valve, FEX, LLVM, and dependency authors retain their respective rights and attribution.

The release includes:

- Exact full Valve Wine source at e60892cc2398b0a83c332a2078c7b85e47bdb42b.
- Proton root source/build recipes at bc896217ffcd67f892f952b010f898fe7bd0f0a1.
- Both additional binary-transformation recipes and manifests, a native helper assembly reference, and an equivalent Wine source patch.
- The Wine source patch retains Wine's LGPL terms; it is not relicensed under the root MIT license.
- Relevant Wine and compiler-runtime notices under LICENSES/.

The Proton root archive does not recursively include every submodule of an entire Proton distribution. It is supplied as build context; unchanged runtime binaries are obtained from Steam. The full source of the modified Wine component is supplied separately. SOURCE archive hashes are in source-manifest.json and release-manifest.json. Independently rebuilding Valve's baseline byte-for-byte is not claimed.

BNet and its credited GameNative authors helped establish the original diagnosis. Those earlier files and their notices remain in scrubbed Git history. This current official-base overlay does not contain BNet or GE-Proton runtime components. This project is not an official release or endorsement from Valve, Wine, FEX, or ZeniMax.
