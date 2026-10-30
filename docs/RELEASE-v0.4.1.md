# v0.4.1 — Fix ESO launcher startup with fresh prefixes

**Recommended experimental ARM64 runtime.** Download `GE-Proton11-7-ESO-BNet-arm64.tar.gz` and verify it with this release's `SHA256SUMS`.

This update fixes a reproduced startup failure where a new prefix could not keep the ESO launcher open. The correction is in Proton's initial font setup; the existing ESO startup and native-call performance corrections are retained.

## What caused the failure?

The v0.4.0 package rebuilds its Wine template on first use. During that process, ten bundled fonts—including Arial and Tahoma—could be linked into the game prefix after Wine had already built the template's font registry. The files existed, but their registrations were missing. In the reproduced case, the 32-bit Bethesda launcher encountered a stack overflow and closed.

An established prefix could already contain the registrations from an earlier runtime. The test handheld's working prefix had them, and a clean official Proton 11.0-2e ARM64 control supplied them too. This explains how the same BNet runtime could work with an established prefix while failing with a new one. The Odin 3 report prompted the investigation, but the fix has not yet been validated on that device.

The runtime makes the fonts available **before Wine initializes its template**, so new prefixes receive the registrations automatically. No additional font download is required.

## Install and start fresh

1. Close ESO and fully exit Steam. Back up any prefix settings or add-ons you want to keep.
2. Preserve the old runtime folder outside `compatibilitytools.d`, then extract the fixed runtime into a fresh destination under `~/.local/share/Steam/compatibilitytools.d/`. Do not merge it into an existing tool folder.
3. Restart Steam and select **GE-Proton11-7 ESO BNet (ARM64, experimental)** for ESO.
4. For a clean reset, close ESO and move or rename its `steamapps/compatdata/306130` folder so that the exact `306130` path no longer exists. Keep the backup until the replacement setup works.
5. Launch ESO normally. Steam recreates the prefix and runs its first-time prerequisites, which can take longer than a subsequent launch.

Steam's **Developer → Delete Proton Files** option did not clear the active prefix in our Armada test. Moving the prefix aside and verifying that `compatdata/306130` was absent did produce a working first launch. This is an observation about the tested setup, not a claim that the menu option fails everywhere.

Steam's Linux ARM64 runtime and FEX rootfs remain prerequisites. Armada automatically restored its standard launch wrapper during testing; no custom font-related launch options were needed.

## Keep an existing prefix instead

An affected prefix can also be repaired without resetting its local settings. With ESO and its Wine processes closed, run the helper included in the runtime:

```sh
python3 "$HOME/.local/share/Steam/compatibilitytools.d/GE-Proton11-7-ESO-BNet-arm64/eso-bnet/repair-launcher-fonts.py" "$HOME/.local/share/Steam/steamapps/compatdata/306130"
```

Adjust the paths for a different Steam installation or library. The helper adds only missing registrations for the ten existing font files and saves a byte-for-byte registry backup first. It preserves existing values, refuses active prefixes and missing fonts, and makes no further changes when run again.

## Validation

- Reproduced the original fresh-prefix failure on a KONKR Pocket FIT Elite running Armada.
- Isolated the font registry key through controlled prefix comparisons and registry bisection.
- Verified that adding only the ten missing font registrations prevents the observed launcher stack overflow.
- Tested the automatic fix with both a fresh runtime template and a fresh game prefix, then confirmed the full launcher with PLAY available through Steam.
- Received user confirmation that the fresh fixed setup worked in-game.
- Repeated the manual prefix reset and received confirmation that the subsequent first launch worked.
- Passed repair safety tests covering backup preservation, idempotence, missing fonts, duplicate registry sections, and active prefixes.
- Independently verified the release archive's indexed files, symlinks and all six pinned Wine/FEX components.

The in-game session duration was not specified. These results do not establish long-session stability or compatibility on other devices.

## Runtime components and credits

The GE-Proton11-7/BNet1 base, graphics components, FEX translation binaries, and both ESO DLL corrections are unchanged. This update changes the Python launcher initialization and adds repair/reproduction helpers. ESO's executable is not modified.

Upstream credit remains with [mrdidit's BNet project](https://github.com/mrdidit/bnet-arm), Dmage22, GameNative contributors, GloriousEggroll, Wine, FEX, and the other component authors. Existing notices and corresponding-source requirements are retained; the additional font-fix source is included in the runtime.

## Rollback

Close ESO, select the previous compatibility tool, and restore the matching prefix backup if needed. Keep the old runtime and prefix backups until the replacement setup has been checked.

## Downloads and sources

The release includes the complete runtime, `ESO-BNet-v0.4.1-patch-sources.tar.gz`, all three original BNet/GE corresponding-source archives, source and release manifests, and `SHA256SUMS`. The repair, launcher transformation, packaging and test scripts are also maintained in the main repository under `bnet/`.

The final runtime retains the exact Proton launcher change tested in the candidate. Release metadata, included documentation and additional source files were finalized for v0.4.1; the outer archive therefore has a new checksum. Use the attached `SHA256SUMS` for the release download.
