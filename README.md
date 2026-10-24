# ESO on Armada OS: Wine ARM64EC import-thunk fix

An experimental compatibility fix for **The Elder Scrolls Online's `0x1100` self-exit after about 305 seconds** on Linux ARM64 using **GE-Proton11-7-Bnet1-arm64** and FEX.

**[Download the complete compiled tool](https://github.com/dxu16/eso-arm64ec-wine-fix/releases/download/v0.1.0-experimental/GE-Proton11-7-ESO-Hotpatch-arm64.tar.gz)** · [Checksums](https://github.com/dxu16/eso-arm64ec-wine-fix/releases/download/v0.1.0-experimental/SHA256SUMS) · [Experimental release and corresponding sources](https://github.com/dxu16/eso-arm64ec-wine-fix/releases/tag/v0.1.0-experimental)

ESO's startup API-entry checks classify legitimate Wine ARM64EC `kernel32.dll` import thunks as inline hooks. This patch gives those thunks the hotpatch entry prolog used by working x64 Wine. **No FEX modification or ESO file modification is required for this particular exit.**

## Tested outcome

Two patched runs reached the animated **“Press A to Start”** screen and survived a 420-second test timeout. One used the original BNet FEX, ntdll, and kernelbase, with only kernel32 changed. The startup capture had no reported API hooks and no five-minute shutdown thread.

**Login, server connection, gameplay, long sessions, and other runtime versions remain untested.** The tests used conservative FEX settings; performance has not been evaluated. This is an experimental compatibility fix, not an official BNet, Wine, or FEX release.

## Install

Download the complete compiled tool and matching source assets from the [experimental release](https://github.com/dxu16/eso-arm64ec-wine-fix/releases/tag/v0.1.0-experimental). The large archives are release downloads, not files in the Git checkout. Alternatively, create the same separate tool from your existing BNet installation:

```bash
python3 scripts/install.py \
  --base "$HOME/.local/share/Steam/compatibilitytools.d/GE-Proton11-7-Bnet1-arm64"
```

The installer checks the exact baseline component hashes and creates **GE-Proton11-7-ESO-Hotpatch-arm64** beside BNet. It never overwrites the base tool or an existing destination. [Installation, prefix preparation, launch, and rollback](docs/INSTALL.md).

For the conservative settings used in testing, run on the handheld:

```bash
bash scripts/launch-eso.sh
```

This launcher creates a separate ESO prefix. It does not edit Steam's compatibility selection. Restarting Steam also makes the installed tool selectable as **GE-Proton11-7-ESO Hotpatch (ARM64, experimental)**, but using an existing Steam prefix has not been validated.

## Repository contents

| Path | Purpose |
| --- | --- |
| `bin/kernel32-eso-hotpatch.dll` | Tested, compiled ARM64X DLL |
| `patches/kernel32-hotpatch-thunks.json` | Exact original/replacement bytes for 796 imported-export slots |
| `scripts/reproduce-kernel32-hotpatch.py` | Deterministic, version-checked binary transformation |
| `scripts/install.py` | Creates a separate compatibility tool from matching BNet |
| `scripts/launch-eso.sh` | Portable launcher with an isolated prefix and tested settings |
| `scripts/fetch-sources.py` | Retrieves and verifies the three corresponding BNet/GE source assets |
| `scripts/verify.py` | Checks repository artifacts and release assets |
| `docs/FINDINGS.md` | Trigger, implementation, controls, and negative experiments |
| `evidence/` | Sanitized validation and provenance records |
| `release-assets/` | Full compiled tool and corresponding source archives; excluded from Git |

No ESO executables, decrypted game code, raw game memory dumps, credentials, or SSH keys are included. Large archives belong in GitHub Releases rather than Git history.

## Reproduce the compiled patch

```bash
python3 scripts/reproduce-kernel32-hotpatch.py \
  /path/to/original/kernel32.dll /path/to/new/kernel32.dll
python3 scripts/verify.py
```

This is a reproducible **post-link binary transformation**, not a source-level Wine fix or a claim of a bit-for-bit Wine build. [Build and provenance](docs/BUILD.md) · [Validation](docs/VALIDATION.md) · [Release checklist](docs/RELEASING.md).

## Attribution and licenses

Based on [mrdidit's BNet1](https://github.com/mrdidit/bnet-arm/releases/tag/BNet1), [GE-Proton](https://github.com/GloriousEggroll/proton-ge-custom), Wine, FEX, and the GameNative fixes credited by BNet. Original fix authors and upstream notices are retained in [`LICENSES/`](LICENSES/).

The compiled Wine DLL retains Wine's LGPL terms. New helper scripts and documentation use the scoped MIT license in [LICENSE](LICENSE). Third-party binaries and copied notices are not relicensed. [Source distribution and licensing](docs/SOURCES-AND-LICENSES.md).
