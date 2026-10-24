#!/usr/bin/env bash
# New isolated prefix; no Steam compatibility setting changes.
set -euo pipefail
STEAM_ROOT="${STEAM_ROOT:-$HOME/.local/share/Steam}"
PROTON="${ESO_PROTON_PATH:-$STEAM_ROOT/compatibilitytools.d/GE-Proton11-7-ESO-Hotpatch-arm64}"
RUNTIME="$STEAM_ROOT/steamapps/common/SteamLinuxRuntime_4-arm64"
GAME="${ESO_GAME_PATH:-$STEAM_ROOT/steamapps/common/Zenimax Online/The Elder Scrolls Online/game/client/eso64.exe}"
COMPAT="${ESO_COMPAT_DATA_PATH:-$HOME/.local/share/eso-arm64ec-wine-fix/compatdata}"
EXPECTED=5b9c2d116f93a307e7b69c31544e52b7a5081fa7caa384020b1c09f948664d5b
ACTUAL=$(sha256sum "$PROTON/files/lib/wine/aarch64-windows/kernel32.dll")
[[ ${ACTUAL%% *} == "$EXPECTED" ]] || { printf 'Unexpected kernel32 build.\n' >&2; exit 2; }
for required in "$PROTON/proton" "$RUNTIME/run" "$GAME"; do
    [[ -f "$required" ]] || { printf 'Missing required file: %s\n' "$required" >&2; exit 2; }
done
mkdir -p "$COMPAT"
if ! mkdir "$COMPAT/.launch.lock"; then
    printf 'Another launch is active, or a stale lock exists: %s\n' "$COMPAT/.launch.lock" >&2
    exit 2
fi
trap 'rmdir "$COMPAT/.launch.lock"' EXIT
mkdir -p "$COMPAT/pfx"
# Existing prefixes do not always refresh DLLs when only a runtime payload changes.
# Prepare only this launcher's explicitly selected prefix, never the Steam game prefix.
python3 - "$PROTON" "$COMPAT" <<'PY'
from pathlib import Path
import shutil, sys
runtime = Path(sys.argv[1]).resolve()
prefix = Path(sys.argv[2]).resolve() / 'pfx'
if not (prefix / 'drive_c').exists():
    shutil.copytree(runtime / 'files/share/default_pfx_arm64', prefix, dirs_exist_ok=True, symlinks=True)
target = prefix / 'drive_c/windows/system32/kernel32.dll'
if not target.parent.resolve().is_relative_to(prefix):
    raise SystemExit('Unexpected external prefix directory symlink')
target.unlink(missing_ok=True)
shutil.copy2(runtime / 'files/lib/wine/aarch64-windows/kernel32.dll', target)
PY
export DISPLAY="${DISPLAY:-:1}" XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
export SteamAppId=306130 SteamGameId=306130
export STEAM_COMPAT_CLIENT_INSTALL_PATH="$STEAM_ROOT" STEAM_COMPAT_DATA_PATH="$COMPAT"
export PROTON_LOG=0 WINEDEBUG=-all FEX_SILENTLOG=1
export FEX_SMC_CHECKS=full FEX_TSOENABLED=1 FEX_VECTORTSOENABLED=1
export FEX_MEMCPYSETTSOENABLED=1 FEX_HALFBARRIERTSOENABLED=0
export FEX_X87REDUCEDPRECISION=0 FEX_MULTIBLOCK=0
cd "${GAME%/*}"
"$RUNTIME/run" -- "$PROTON/proton" run "$GAME" "$@"
