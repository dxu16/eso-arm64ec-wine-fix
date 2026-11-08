#!/usr/bin/env python3
"""Build v0.4.2 from the exact v0.4.1 archive and current wrapper sources."""

import argparse
import gzip
import hashlib
import io
from pathlib import Path
import runpy
import tarfile

import runtime


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
INPUT_SHA256 = "b0baff9b9fe2996e648030e74ff19d5a8aa803b5ddd6c5a191c354110e8842d6"
transform_manifest = runpy.run_path(str(HERE / "install-probe-wrapper.py"))["manifest_with_wrapper"]


def package(source_path, destination):
    if destination.exists() or source_path.resolve() == destination.resolve():
        raise ValueError("Choose a new, separate output archive")
    with source_path.open("rb") as source:
        if hashlib.file_digest(source, "sha256").hexdigest() != INPUT_SHA256:
            raise ValueError("Expected the exact public v0.4.1 runtime archive")
    replacements = {
        "eso-bnet/README.md": (ROOT / "README.md").read_bytes(),
        "probe-wrapper.py": (HERE / "probe-wrapper.py").read_bytes(),
        "version": b"1789520806 GE-Proton11-7-ESO-BNet-arm64-v0.4.2\n",
        "README-ESO.txt": b"GE-Proton11-7 ESO BNet ARM64 v0.4.2. Extract into ~/.local/share/Steam/compatibilitytools.d/ and restart Steam. See eso-bnet/docs/INSTALL.md. Sources and release: https://github.com/dxu16/eso-arm64ec-wine-fix/releases/tag/v0.4.2\n",
    }
    for path in sorted((ROOT / "docs").rglob("*")):
        if path.is_file():
            replacements["eso-bnet/docs/" + path.relative_to(ROOT / "docs").as_posix()] = path.read_bytes()
    for name in ("probe-wrapper.py", "install-probe-wrapper.py", "test_probe_wrapper.py", "package-probe-safe-runtime.py"):
        replacements["eso-bnet/" + name] = (HERE / name).read_bytes()
    digests = {}
    with destination.open("xb") as output, gzip.GzipFile(filename="", fileobj=output, mode="wb", compresslevel=3, mtime=0) as compressed, tarfile.open(fileobj=compressed, mode="w|") as target:
        def add(name, data, mode=0o644):
            member = tarfile.TarInfo(runtime.TOOL_ID + "/" + name)
            member.mode = mode
            member.size = len(data)
            target.addfile(member, io.BytesIO(data))
            digests[name] = hashlib.sha256(data).hexdigest()

        with tarfile.open(source_path, "r|gz") as source:
            for member in source:
                name = runtime.safe_name(member.name)
                if name == runtime.INDEX:
                    continue
                if not member.isfile():
                    target.addfile(member)
                    continue
                data = source.extractfile(member).read()
                if name == "toolmanifest.vdf":
                    data = transform_manifest(data.decode()).encode()
                elif name == "RUNTIME-SOURCES.txt":
                    data = data.replace(b"v0.4.1", b"v0.4.2")
                    data += b"\nGraphics-probe isolation source: probe-wrapper.py and eso-bnet/install-probe-wrapper.py. Wine/FEX binaries retain their pinned hashes.\n"
                elif name in replacements:
                    data = replacements.pop(name)
                add(name, data, member.mode)
        for name, data in sorted(replacements.items()):
            add(name, data, 0o755 if name == "probe-wrapper.py" else 0o644)
        index = "".join(value + "  " + name + "\n" for name, value in sorted(digests.items())).encode()
        add(runtime.INDEX, index)
    return runtime.verify(destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    arguments = parser.parse_args()
    print(package(arguments.input, arguments.output))


if __name__ == "__main__":
    main()
