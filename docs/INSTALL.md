# Install and rollback

Requirements: Linux ARM64, Python 3.9+, GNU tar/gzip, Steam and its
SteamLinuxRuntime_4-arm64 runtime, the exact supported BNet build, and an
existing ESO installation. This is not a Windows DLL replacement.

Stop ESO before installation or prefix preparation.

## Complete compiled tool

From the repository root, verify the bundled assets and extract the tool:

For a Git checkout, first download the complete runtime, three source archives,
and SHA256SUMS from the [experimental release](https://github.com/dxu16/eso-arm64ec-wine-fix/releases/tag/v0.1.0-experimental)
into `release-assets/`. The source archives can also be obtained with
`python3 scripts/fetch-sources.py`. The repository's `release-manifest.json`
records the expected hashes.

```bash
python3 scripts/verify.py --release-assets
mkdir -p "$HOME/.local/share/Steam/compatibilitytools.d"
# Confirm that the destination tool folder does not already exist first.
test ! -e "$HOME/.local/share/Steam/compatibilitytools.d/GE-Proton11-7-ESO-Hotpatch-arm64"
tar -xzf release-assets/GE-Proton11-7-ESO-Hotpatch-arm64.tar.gz \
  -C "$HOME/.local/share/Steam/compatibilitytools.d"
```

Run commands individually and stop if a command fails. Extraction creates a
separate tool. Do not extract over a previous installation.

## Build the tool from an installed BNet runtime

```bash
python3 scripts/install.py \
  --base "$HOME/.local/share/Steam/compatibilitytools.d/GE-Proton11-7-Bnet1-arm64"
```

This copies the complete base, replaces kernel32 in its ARM64 runtime and
default ARM64 prefix template, and sets a separate tool ID/display name.
It does not modify an existing game prefix.

## Launch

```bash
bash scripts/launch-eso.sh
```

The launcher prepares its own prefix under
`~/.local/share/eso-arm64ec-wine-fix/compatdata`, including the corrected DLL.
It uses the conservative settings in [VALIDATION.md](VALIDATION.md). Steam
must be available for the normal Steam/Proton environment.

Supported overrides:

```bash
ESO_GAME_PATH="/other/library/Zenimax Online/The Elder Scrolls Online/game/client/eso64.exe" \
ESO_PROTON_PATH="/other/path/GE-Proton11-7-ESO-Hotpatch-arm64" \
ESO_COMPAT_DATA_PATH="$HOME/.local/share/eso-arm64ec-wine-fix/my-prefix" \
bash scripts/launch-eso.sh
```

Use a dedicated prefix for `ESO_COMPAT_DATA_PATH`. Do not point it at the
Steam ESO prefix or another running Wine prefix. The launcher replaces the
selected prefix's kernel32 before starting the game. A directory lock prevents
concurrent launches through this script; remove a stale lock only after
confirming that its game has stopped.

`scripts/launch-tested-prefix.sh` records the original diagnostic launcher
and its directory layout. Following the investigation cleanup, that prefix
and diagnostic directory are archived on the investigator's PC, so this
historical launcher is no longer a live launch path on the device. The working
runtime was moved into Steam's compatibilitytools.d directory. Use the
portable launcher above with a fresh, separate prefix.

## Steam selection

After restarting Steam, the new tool appears as
**GE-Proton11-7-ESO Hotpatch (ARM64, experimental)**. The installer does not
select it automatically. Existing Steam prefixes may retain the old DLL;
the validated result used an explicitly prepared isolated prefix. A normal
Steam launch using an existing prefix is not yet part of the verified result.

## Rollback

Exit the experimental game and return to your existing Steam launch and BNet
selection. The base runtime, Steam game prefix, and ESO installation were not
changed by the installer. Keep experimental prefixes if you want to retain
their normal ESO-generated settings; remove them manually only when no
longer needed.
