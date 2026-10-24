# ESO ARM64EC Wine fix v0.1.0 — experimental

This release addresses ESO's repeatable `0x1100` self-exit around 305 seconds
on the tested Armada OS / GE-Proton11-7-Bnet1-arm64 setup.

Wine's legitimate ARM64EC kernel32 imported-export jump thunks triggered
ESO's API-entry hook checks. Adding the hotpatch entry prolog used by working
x64 Wine prevented those reports and the delayed shutdown. Function addresses,
import targets, implementations, and native ARM64 code are preserved.

## Downloads

- **GE-Proton11-7-ESO-Hotpatch-arm64.tar.gz**: complete compiled Steam compatibility tool, approximately 708 MB.
- **SHA256SUMS** and **release-manifest.json**: file hashes and sizes.
- **Bnet1-component-sources.tar.gz**, **GE-Proton11-7-upstream-sources.tar.zst**, and **GE-Proton11-7-extras-sources.tar.zst**: unchanged corresponding baseline source assets.
- GitHub's repository source archives contain the additional patch manifest, deterministic transformation script, helper scripts, documentation, and notices.

## Install

Verify the downloaded runtime against SHA256SUMS. Extract the tool into
`~/.local/share/Steam/compatibilitytools.d/` without overwriting an existing
tool. Restart Steam to see **GE-Proton11-7-ESO Hotpatch (ARM64, experimental)**.
The repository also supplies an installer from a matching BNet1 installation
and a portable launcher using a separate Wine prefix and the tested FEX settings.
See [installation instructions](https://github.com/dxu16/eso-arm64ec-wine-fix/blob/main/docs/INSTALL.md).

## Validation and limits

Two patched runs reached the animated “Press A to Start” screen and survived
a 420-second test timeout. The minimal run used original BNet FEX, ntdll,
and kernelbase; only Wine's kernel32 and its default-prefix copy were changed.

**Login, server connection, gameplay, long-session stability, performance,
other devices, other game versions, and other runtime versions remain untested.**
Existing Steam prefixes may need their builtin DLLs refreshed; the verified
result used an explicitly prepared isolated prefix. The original ARM64EC
thunks are valid code; this is an entry-layout compatibility workaround.

Patched kernel32 SHA256:

```text
5b9c2d116f93a307e7b69c31544e52b7a5081fa7caa384020b1c09f948664d5b
```

Wine, BNet, GE-Proton, FEX, and dependency notices are retained. This is not an
official upstream release. No ESO executable, decrypted game code, raw game
memory, credentials, or private device backups are included.
