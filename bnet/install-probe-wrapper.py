#!/usr/bin/env python3
"""Install graphics-probe isolation in an existing, idle Proton tool."""

import argparse
import hashlib
import os
from pathlib import Path
import re
import shutil


def manifest_with_wrapper(original):
    pattern = r'("commandline"\s+")/(?:proton|probe-wrapper\.py)(\s+%verb%")'
    updated, count = re.subn(pattern, r'\1/probe-wrapper.py\2', original)
    if count != 1:
        raise ValueError("Expected one standard Proton commandline in toolmanifest.vdf")
    return updated


def install(runtime, wrapper):
    runtime = runtime.resolve(strict=True)
    manifest = runtime / "toolmanifest.vdf"
    updated = manifest_with_wrapper(manifest.read_text(encoding="utf-8"))
    if not (runtime / "proton").is_file():
        raise ValueError("Missing Proton entry point")
    # Validate every existing index before making a change.
    indexes = [runtime / name for name in (
        "bnet/SHA256SUMS", "eso-comparison/RUNTIME-SHA256SUMS", "eso-bnet/RUNTIME-SHA256SUMS"
    ) if (runtime / name).is_file()]
    entries = {}
    for index in indexes:
        rows = {}
        for line in index.read_text().splitlines():
            expected, relative = line.split("  ", 1)
            path = runtime / relative
            if not path.resolve().is_relative_to(runtime) or not path.is_file():
                raise ValueError("Invalid indexed runtime path: " + relative)
            if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                raise ValueError("Runtime checksum mismatch: " + relative)
            rows[relative] = expected
        entries[index] = rows
    target = runtime / "probe-wrapper.py"
    temporary = runtime / ".probe-wrapper.py.tmp"
    shutil.copyfile(wrapper, temporary)
    temporary.chmod(0o755)
    os.replace(temporary, target)
    temporary = manifest.with_name(".toolmanifest.vdf.tmp")
    temporary.write_text(updated, encoding="utf-8", newline="\n")
    temporary.chmod(manifest.stat().st_mode & 0o777)
    os.replace(temporary, manifest)
    for index, rows in entries.items():
        for relative in ("probe-wrapper.py", "toolmanifest.vdf"):
            rows[relative] = hashlib.sha256((runtime / relative).read_bytes()).hexdigest()
        temporary = index.with_name(index.name + ".tmp")
        temporary.write_text("".join(digest + "  " + name + "\n" for name, digest in sorted(rows.items())))
        os.replace(temporary, index)
    return {"runtime": str(runtime), "checksum_indexes_updated": len(indexes)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runtime", type=Path)
    parser.add_argument("--wrapper", type=Path, default=Path(__file__).with_name("probe-wrapper.py"))
    arguments = parser.parse_args()
    print(install(arguments.runtime, arguments.wrapper))


if __name__ == "__main__":
    main()
