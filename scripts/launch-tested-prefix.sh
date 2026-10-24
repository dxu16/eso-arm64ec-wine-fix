#!/usr/bin/env bash
# Isolated ESO runtime: original BNet FEX/ntdll + Wine import-thunk hotpatch prologs.
set -euo pipefail
DIAG_ROOT="$HOME/eso-fex-investigation"
STEAM_ROOT="$HOME/.local/share/Steam"
PROTON="$DIAG_ROOT/GE-Proton11-7-ESO-Hotpatch-arm64"
RUNTIME="$STEAM_ROOT/steamapps/common/SteamLinuxRuntime_4-arm64"
GAME="$STEAM_ROOT/steamapps/common/Zenimax Online/The Elder Scrolls Online/game/client/eso64.exe"
EXPECTED=5b9c2d116f93a307e7b69c31544e52b7a5081fa7caa384020b1c09f948664d5b
ACTUAL=$(sha256sum "$PROTON/files/lib/wine/aarch64-windows/kernel32.dll")
[[ ${ACTUAL%% *} == "$EXPECTED" ]] || { printf 'Unexpected kernel32 build; refusing launch.\n' >&2; exit 2; }
export DISPLAY="${DISPLAY:-:1}" XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
export SteamAppId=306130 SteamGameId=306130
export STEAM_COMPAT_CLIENT_INSTALL_PATH="$STEAM_ROOT"
export STEAM_COMPAT_DATA_PATH="$DIAG_ROOT/compat-eso-hotpatch-stock"
export PROTON_LOG=0 WINEDEBUG=-all FEX_SILENTLOG=1
export FEX_SMC_CHECKS=full FEX_TSOENABLED=1 FEX_VECTORTSOENABLED=1
export FEX_MEMCPYSETTSOENABLED=1 FEX_HALFBARRIERTSOENABLED=0
export FEX_X87REDUCEDPRECISION=0 FEX_MULTIBLOCK=0
cd "${GAME%/*}"
exec "$RUNTIME/run" -- "$PROTON/proton" run "$GAME" "$@"
