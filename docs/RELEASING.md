# GitHub publication layout

Repository: [dxu16/eso-arm64ec-wine-fix](https://github.com/dxu16/eso-arm64ec-wine-fix).
The initial experimental release tag is `v0.1.0-experimental`.

Commit the README, documentation, scripts, manifest, small compiled DLL,
licenses, evidence, source pins, checksum manifest, and CI workflow. Keep
`release-assets/` archives out of Git history; the included `.gitignore`
already does this.

Before publishing:

```bash
python3 scripts/verify.py --release-assets
bash -n scripts/launch-eso.sh scripts/launch-tested-prefix.sh
```

Create an experimental release in the intended repository and upload all
four archives listed in `release-assets/README.md`, plus its SHA256SUMS.
Include `release-manifest.json` as a release asset as well. Upload and verify
all assets in a draft before publishing the release as a prerelease.
Use the existing findings/validation text for the release notes. State that
testing reached the title screen only, that the correction is version-bound,
and that it is a post-link Wine compatibility fix rather than a FEX patch.

The source archives are intentionally duplicated from BNet's pinned release
so the corresponding source assets accompany this derived runtime. Retain
the repository source snapshot and all third-party notices with the release.

Do not upload the original investigation workspace, ESO executable, game
memory dumps, decrypted protection code, SSH material, or account data.
