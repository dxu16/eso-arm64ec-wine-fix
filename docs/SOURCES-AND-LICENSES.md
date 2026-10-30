# Sources, upstream credit and licenses

The v0.4.1 runtime is derived from **[mrdidit/bnet-arm](https://github.com/mrdidit/bnet-arm)**, specifically [BNet1](https://github.com/mrdidit/bnet-arm/releases/tag/BNet1), on [GloriousEggroll's GE-Proton11-7](https://github.com/GloriousEggroll/proton-ge-custom/releases/tag/GE-Proton11-7). BNet's work is upstream work, not new FEX/Wine compatibility work claimed by this ESO project.

The original Blizzard Wine fixes are by [Dmage22](https://github.com/GameNative/proton-wine/pull/47). [GameNative's Wine integration](https://github.com/GameNative/proton-wine/pull/67) and its pinned FEX series include work by Dmage22, tarikbc and Utkarsh Dalal. Wine, FEX, GE-Proton, LLVM and other dependency authors retain their copyright and license terms. Exact revisions, patch ordering and hashes are in `bnet/upstream-source-pins.json`; copies of the original patches retain their attribution under `bnet/patches/`.

The release carries the same three corresponding-source downloads as BNet1, verified against their original SHA256 hashes:

- `Bnet1-component-sources.tar.gz`: prepared Wine/FEX sources, original patches, dependencies, build recipes and notices.
- `GE-Proton11-7-upstream-sources.tar.zst`: GE sources, non-FEX submodules, preparation, Mono and Gecko sources.
- `GE-Proton11-7-extras-sources.tar.zst`: additional GE component sources and locked crates.

It also supplies `ESO-BNet-v0.4.1-patch-sources.tar.gz` with this project's exact post-link recipes, manifests, native assembly reference, equivalent Wine source patch, attribution and release evidence. `bnet/source-manifest.json` records the original source URLs, sizes and hashes. These actual source assets accompany the release; branch links are not used as a substitute.

Wine DLLs and Wine-derived patches/assembly retain LGPL-2.1-or-later terms. FEX retains its MIT terms; GE and dependencies retain their own terms. The repository MIT license applies to original project helpers/documentation, not third-party runtime binaries or Wine-derived code. The runtime preserves GE root notices and adds upstream component notices under `eso-bnet/LICENSES/runtime/`.

Wine was not recompiled for the two ESO changes. Rebuilding the original entire baseline byte-for-byte is not claimed. The exact transformation is reproducible from the pinned precompiled DLLs with `bnet/reproduce.py`. Steam's external ARM64 runtime/rootfs are prerequisites and are not bundled.

The older Valve source indexes at repository root and `scripts/` are historical v0.3.0 material. See [legacy source details](legacy-valve/SOURCES-AND-LICENSES.md).
