#!/usr/bin/env python3
"""Keep Steam's automatic graphics probes out of shared Proton prefixes."""

import hashlib
import os
from pathlib import Path
import signal
import subprocess
import sys


PROBE_NAMES = {"d3ddriverquery.exe", "d3ddriverquery64.exe"}
LAUNCH_VERBS = {"run", "waitforexitandrun", "runinprefix"}


def probe_name(arguments):
    if len(arguments) < 2 or arguments[0] not in LAUNCH_VERBS:
        return None
    name = arguments[1].replace("\\", "/").rsplit("/", 1)[-1].lower()
    return name if name in PROBE_NAMES else None


def probe_directory(runtime, arguments, environment):
    cache = Path(environment.get("XDG_CACHE_HOME", ""))
    if not cache.is_absolute():
        cache = Path.home() / ".cache"
    identity = hashlib.sha256(os.fsencode(runtime)).hexdigest()[:16]
    api = "d3d12" if "-d3d12" in arguments[2:] else "d3d11"
    return cache / "proton-graphics-probes" / identity / (probe_name(arguments) + "-" + api)


def run_probe(proton, arguments, directory):
    import fcntl

    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    lock_path = directory.with_name(directory.name + ".lock")
    environment = os.environ.copy()
    environment["STEAM_COMPAT_DATA_PATH"] = str(directory)
    environment["WINEPREFIX"] = str(directory / "pfx")
    descriptor = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    with os.fdopen(descriptor, "a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        process = subprocess.Popen([str(proton), *arguments], env=environment)

        def forward_signal(number, frame):
            try:
                process.send_signal(number)
            except ProcessLookupError:
                pass

        previous = {}
        try:
            for number in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
                previous[number] = signal.signal(number, forward_signal)
            result = process.wait()
        finally:
            for number, handler in previous.items():
                signal.signal(number, handler)
    return result if result >= 0 else 128 - result


def main():
    runtime = Path(__file__).resolve().parent
    proton = runtime / "proton"
    arguments = sys.argv[1:]
    if probe_name(arguments) is None:
        os.execv(str(proton), [str(proton), *arguments])
    directory = probe_directory(runtime, arguments, os.environ)
    return run_probe(proton, arguments, directory)


if __name__ == "__main__":
    sys.exit(main())
