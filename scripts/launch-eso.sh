#!/usr/bin/env bash
# New isolated prefix; no Steam compatibility setting changes.
set -euo pipefail
STEAM_ROOT="${STEAM_ROOT:-$HOME/.local/share/Steam}"
PROTON="${ESO_PROTON_PATH:-$STEAM_ROOT/compatibilitytools.d/Proton-11.0-ESO-Official-Hotpatch-arm64}"
RUNTIME="$STEAM_ROOT/steamapps/common/SteamLinuxRuntime_4-arm64"
GAME="${ESO_GAME_PATH:-$STEAM_ROOT/steamapps/common/Zenimax Online/The Elder Scrolls Online/game/client/eso64.exe}"
COMPAT="${ESO_COMPAT_DATA_PATH:-$HOME/.local/share/eso-arm64ec-wine-fix/compatdata}"
PREFIX_SOURCE="${ESO_PREFIX_SOURCE:-$STEAM_ROOT/steamapps/compatdata/306130}"
EXPECTED=dbf5fa3a80204259f8e42e9a4ebcbdd6769f3f86301aa9da39f22797e0e40257
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
python3 - "$PROTON" "$COMPAT" "$PREFIX_SOURCE" <<'PY'
from pathlib import Path
import shutil, stat, sys
runtime = Path(sys.argv[1]).resolve()
prefix = Path(sys.argv[2]).resolve() / 'pfx'
source = Path(sys.argv[3]).resolve()
if source == prefix.parent or source in prefix.parent.parents or prefix.parent in source.parents:
    raise SystemExit('Source and destination compatibility directories must be separate and non-overlapping')
seed_guard = prefix.parent / '.source-copy-in-progress'
if seed_guard.exists():
    raise SystemExit('An earlier prefix import was interrupted; choose a new empty ESO_COMPAT_DATA_PATH')
if not (prefix / 'drive_c').exists():
    if not (source / 'pfx/drive_c').is_dir():
        raise SystemExit('Launch ESO once through Steam to install its prerequisites, close it, then rerun; or set ESO_PREFIX_SOURCE to a Steam-initialized ESO compatibility directory')
    if (source / '.launch.lock').exists():
        raise SystemExit('Source launcher lock is present; close the source game first')
    def ignore_runtime_nodes(directory, names):
        ignored = []
        for name in names:
            path = Path(directory) / name
            if Path(directory).resolve() == source and name in {'fex-emu', 'pfx.lock', '.launch.lock'}:
                ignored.append(name)
                continue
            mode = path.lstat().st_mode
            if not (stat.S_ISREG(mode) or stat.S_ISDIR(mode) or stat.S_ISLNK(mode)):
                ignored.append(name)
        return ignored
    seed_guard.write_text('Prefix import is incomplete until this marker is removed.\n')
    shutil.copytree(source, prefix.parent, dirs_exist_ok=True, symlinks=True, ignore=ignore_runtime_nodes)
    seed_guard.unlink()
for name in ['kernel32.dll', 'ntdll.dll', 'kernelbase.dll', 'libarm64ecfex.dll', 'libwow64fex.dll']:
    target = prefix / 'drive_c/windows/system32' / name
    if not target.parent.resolve().is_relative_to(prefix):
        raise SystemExit('Unexpected external prefix directory symlink')
    target.unlink(missing_ok=True)
    shutil.copy2(runtime / 'files/lib/wine/aarch64-windows' / name, target)
PY
export DISPLAY="${DISPLAY:-:1}" XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
export SteamAppId=306130 SteamGameId=306130
export STEAM_COMPAT_CLIENT_INSTALL_PATH="$STEAM_ROOT" STEAM_COMPAT_DATA_PATH="$COMPAT"
export PROTON_LOG=0 WINEDEBUG="${ESO_WINEDEBUG:--all}" FEX_SILENTLOG=1
export FEX_SMC_CHECKS=full FEX_TSOENABLED=1 FEX_VECTORTSOENABLED=1
export FEX_MEMCPYSETTSOENABLED=1 FEX_HALFBARRIERTSOENABLED=0
export FEX_X87REDUCEDPRECISION=0 FEX_MULTIBLOCK=0
cd "${GAME%/*}"
"$RUNTIME/run" -- "$PROTON/proton" run "$GAME" "$@"
