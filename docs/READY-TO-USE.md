# Ready-to-use BNet runtime

The font-fixed complete runtime is `GE-Proton11-7-ESO-BNet-arm64.tar.gz` from [v0.4.1](https://github.com/dxu16/eso-arm64ec-wine-fix/releases/tag/v0.4.1). [Release notes](RELEASE-v0.4.1.md). Follow [INSTALL.md](INSTALL.md).

The archive has one tool folder, canonical ownership/timestamps, safe relative symlinks, all runtime licenses, and an internal per-file SHA256 index. It excludes generated prefixes, registries from those prefixes, bytecode caches, device settings, and logs from the investigation.

Run `python3 -B bnet/runtime.py /path/to/GE-Proton11-7-ESO-BNet-arm64.tar.gz` from this repository to verify all indexed files and the six pinned Wine/FEX components without extracting or executing the runtime. Verification requires no additional Python packages.

The release also supplies a small patch-source archive and the three original BNet/GE corresponding-source archives. Those are developer downloads; they are not needed to play. No game executable, game data, Steam account data, or configured Wine prefix is included.
