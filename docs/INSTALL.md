# Install and rollback

## Requirements

Linux ARM64, Python 3.9+, Steam, SteamLinuxRuntime_4-arm64, an existing ESO installation, and **Valve Proton 11.0-2e ARM64**. [Official Proton release](https://github.com/ValveSoftware/Proton/releases/tag/proton-11.0-2e).

This is a precompiled overlay plus installer. It is not a standalone copy of Valve's whole runtime. No compiler or BNet installation is required. The supported Steam version string is `1791559733 proton-11.0-2e-arm64`; the installer checks five exact DLL hashes and rejects other builds.

## First-run dependencies

Launch ESO through Steam once using the official ARM64 Proton tool, allow Steam's first-run setup to finish, then close ESO. The bundled ESO install scripts specify Visual C++ 2010 x86/x64 and DirectX June 2010. A fresh Wine prefix is not equivalent to the Steam-initialized prefix used in the decisive tests. The reason for its distinct 0x1101 exit was not isolated.

## Verify and install

Download the overlay and SHA256SUMS from the release. Verify the outer archive before extracting it:

```bash
sha256sum -c SHA256SUMS --ignore-missing
tar -xzf Proton-11.0-ESO-Official-Hotpatch-arm64-overlay.tar.gz
cd eso-arm64ec-wine-fix
python3 scripts/verify.py
python3 scripts/install.py
```

Run commands individually and stop on failure. The installer never overwrites an existing destination. It copies the official runtime, patches kernel32, preserves the official template's relative symlink, retains licenses, and creates a distinct tool ID.

Defaults:

- Base: `~/.local/share/Steam/steamapps/common/Proton 11.0 (ARM64)`
- New tool: `~/.local/share/Steam/compatibilitytools.d/Proton-11.0-ESO-Official-Hotpatch-arm64`

For another Steam library:

```bash
python3 scripts/install.py --base "/other/library/steamapps/common/Proton 11.0 (ARM64)"
```

## Launch with the tested prefix method

Close any running ESO instance, then:

```bash
bash scripts/launch-eso.sh
```

The first run copies the existing Steam ESO compatibility directory into `~/.local/share/eso-arm64ec-wine-fix/compatdata`. It skips FEX server data, sockets, FIFOs, devices, and active-lock files. It then refreshes kernel32, ntdll, kernelbase and both FEX translator DLLs in the clone. Only kernel32 differs from Valve's source runtime. The source Steam prefix is not modified by the helper.

The launcher refuses overlapping source/destination directories and concurrent launches. An interrupted import leaves a marker and requires a new empty destination; it does not silently launch from a partial copy. Remove a stale lock only after checking that its game has stopped.

Overrides:

```bash
ESO_GAME_PATH="/other/library/Zenimax Online/The Elder Scrolls Online/game/client/eso64.exe" ESO_PREFIX_SOURCE="/other/library/steamapps/compatdata/306130" ESO_COMPAT_DATA_PATH="$HOME/.local/share/eso-arm64ec-wine-fix/separate-prefix" ESO_PROTON_PATH="/other/path/Proton-11.0-ESO-Official-Hotpatch-arm64" bash scripts/launch-eso.sh
```

`ESO_PREFIX_SOURCE` is a Steam compatibility directory containing `pfx/drive_c`, not the `pfx` directory itself. Keep it separate from `ESO_COMPAT_DATA_PATH`. The helper replaces five core DLLs only in its selected destination prefix.

Conservative settings match [VALIDATION.md](VALIDATION.md). `ESO_WINEDEBUG` optionally enables diagnostic Wine logging; it defaults to `-all`.

## Steam selection and rollback

Restart Steam to see **Proton 11.0 ESO Hotpatch (official base, ARM64, experimental)**. Selection is not changed automatically. Direct Steam launching using other prefix states has not been separately validated.

For rollback, exit the experimental game and return to your usual official-Proton selection. The installer leaves the original runtime and the launcher leaves the source Steam prefix intact. Keep or remove the experimental tool and its separate prefix when no longer needed.
