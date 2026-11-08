"""Exercise probe routing, process lifetime locking, and normal Proton launches."""

import importlib.util
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("probe_wrapper", HERE / "probe-wrapper.py")
WRAPPER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(WRAPPER)
INSTALL_SPEC = importlib.util.spec_from_file_location("probe_installer", HERE / "install-probe-wrapper.py")
INSTALLER = importlib.util.module_from_spec(INSTALL_SPEC)
INSTALL_SPEC.loader.exec_module(INSTALLER)

FAKE_PROTON = """#!/usr/bin/env python3
import json, os, pathlib, sys, time
output = pathlib.Path(os.environ['TEST_OUTPUT'])
output.write_text(json.dumps({'args':sys.argv[1:], 'data':os.environ.get('STEAM_COMPAT_DATA_PATH'), 'prefix':os.environ.get('WINEPREFIX'), 'keep':os.environ.get('TEST_KEEP')}))
if os.environ.get('TEST_HOLD'):
    marker = pathlib.Path(os.environ['STEAM_COMPAT_DATA_PATH']) / 'active'
    with marker.open('x'):
        time.sleep(float(os.environ['TEST_HOLD']))
    marker.unlink()
if os.environ.get('TEST_WAIT'):
    time.sleep(30)
sys.exit(int(os.environ.get('TEST_EXIT', '0')))
"""


@unittest.skipUnless(os.name == "posix", "Runtime entry points require Linux")
class ProbeWrapperTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="proton-probe-tests-")
        self.root = Path(self.temporary.name)
        self.runtime = self.make_runtime("runtime one")
        self.environment = os.environ.copy()
        self.environment.update({
            "XDG_CACHE_HOME": str(self.root / "cache"),
            "STEAM_COMPAT_DATA_PATH": str(self.root / "original prefix"),
            "WINEPREFIX": str(self.root / "original prefix/pfx"),
            "TEST_OUTPUT": str(self.root / "result.json"),
            "TEST_KEEP": "original environment",
        })

    def tearDown(self):
        self.temporary.cleanup()

    def make_runtime(self, name):
        directory = self.root / name
        directory.mkdir()
        shutil.copy2(HERE / "probe-wrapper.py", directory / "probe-wrapper.py")
        proton = directory / "proton"
        proton.write_text(FAKE_PROTON)
        proton.chmod(0o755)
        return directory

    def start(self, arguments, environment=None, runtime=None):
        return subprocess.Popen(
            [sys.executable, str((runtime or self.runtime) / "probe-wrapper.py"), *arguments],
            env=environment or self.environment,
        )

    def read_result(self, environment=None):
        return json.loads(Path((environment or self.environment)["TEST_OUTPUT"]).read_text())

    def test_normal_launch_preserves_arguments_environment_and_exit(self):
        self.environment["TEST_EXIT"] = "37"
        arguments = ["waitforexitandrun", "/games/ESO with spaces.exe", "literal $value", "a;b"]
        self.assertEqual(self.start(arguments).wait(timeout=5), 37)
        result = self.read_result()
        self.assertEqual(result["args"], arguments)
        self.assertEqual(result["data"], self.environment["STEAM_COMPAT_DATA_PATH"])
        self.assertEqual(result["prefix"], self.environment["WINEPREFIX"])
        self.assertEqual(result["keep"], "original environment")
        self.assertFalse((self.root / "cache").exists())

    def test_only_the_target_executable_is_matched(self):
        self.assertIsNone(WRAPPER.probe_name(["run", "/game.exe", "d3ddriverquery64.exe"]))
        self.assertIsNone(WRAPPER.probe_name(["run", "/fake-d3ddriverquery64.exe"]))
        self.assertIsNone(WRAPPER.probe_name(["getcompatpath", "/d3ddriverquery64.exe"]))
        self.assertIsNone(WRAPPER.probe_name([]))
        self.assertEqual(WRAPPER.probe_name(["run", r"C:\bin\D3DDriverQuery64.EXE"]), "d3ddriverquery64.exe")

    def test_probe_uses_an_isolated_prefix_and_keeps_other_settings(self):
        arguments = ["run", "/steam/bin/d3ddriverquery64.exe", "-d3d12"]
        self.assertEqual(self.start(arguments).wait(timeout=5), 0)
        result = self.read_result()
        self.assertEqual(result["args"], arguments)
        self.assertNotEqual(result["data"], self.environment["STEAM_COMPAT_DATA_PATH"])
        self.assertTrue(result["data"].endswith("d3ddriverquery64.exe-d3d12"))
        self.assertEqual(result["prefix"], str(Path(result["data"]) / "pfx"))
        self.assertEqual(result["keep"], "original environment")

    def test_runtime_api_and_executable_get_distinct_prefixes(self):
        first = ["run", "/bin/d3ddriverquery64.exe"]
        second = [*first, "-d3d12"]
        third = ["run", "/bin/d3ddriverquery.exe"]
        other_runtime = self.make_runtime("runtime two")
        directories = {
            WRAPPER.probe_directory(self.runtime, first, self.environment),
            WRAPPER.probe_directory(self.runtime, second, self.environment),
            WRAPPER.probe_directory(self.runtime, third, self.environment),
            WRAPPER.probe_directory(other_runtime, first, self.environment),
        }
        self.assertEqual(len(directories), 4)
        relative_cache = dict(self.environment, XDG_CACHE_HOME="relative-cache")
        self.assertTrue(WRAPPER.probe_directory(self.runtime, first, relative_cache).is_absolute())

    def test_same_probe_is_locked_for_the_entire_child_lifetime(self):
        self.environment["TEST_HOLD"] = "0.4"
        arguments = ["run", "/bin/d3ddriverquery64.exe"]
        first = self.start(arguments)
        second_environment = dict(self.environment, TEST_OUTPUT=str(self.root / "second.json"))
        second = self.start(arguments, second_environment)
        self.assertEqual(first.wait(timeout=5), 0)
        self.assertEqual(second.wait(timeout=5), 0)
        self.assertEqual(self.read_result()["data"], self.read_result(second_environment)["data"])

    def test_simultaneous_runtimes_never_share_a_prefix(self):
        other_runtime = self.make_runtime("runtime two")
        self.environment["TEST_HOLD"] = "0.4"
        other_environment = dict(self.environment, TEST_OUTPUT=str(self.root / "other.json"))
        arguments = ["run", "/bin/d3ddriverquery64.exe"]
        first = self.start(arguments)
        second = self.start(arguments, other_environment, other_runtime)
        self.assertEqual(first.wait(timeout=5), 0)
        self.assertEqual(second.wait(timeout=5), 0)
        self.assertNotEqual(self.read_result()["data"], self.read_result(other_environment)["data"])

    def test_termination_is_forwarded_and_lock_is_released(self):
        self.environment["TEST_WAIT"] = "1"
        arguments = ["run", "/bin/d3ddriverquery64.exe"]
        process = self.start(arguments)
        try:
            deadline = time.monotonic() + 5
            while not Path(self.environment["TEST_OUTPUT"]).exists() and time.monotonic() < deadline:
                time.sleep(0.02)
            self.assertTrue(Path(self.environment["TEST_OUTPUT"]).exists())
            process.send_signal(signal.SIGTERM)
            self.assertEqual(process.wait(timeout=5), 128 + signal.SIGTERM)
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
        self.environment.pop("TEST_WAIT")
        self.assertEqual(self.start(arguments).wait(timeout=5), 0)


class ProbeInstallerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="proton-probe-install-")
        self.runtime = Path(self.temporary.name)
        (self.runtime / "proton").write_text("original Proton launcher")
        (self.runtime / "toolmanifest.vdf").write_text('"manifest" { "commandline" "/proton %verb%" "use_sessions" "1" }\n')
        index = self.runtime / "eso-bnet/RUNTIME-SHA256SUMS"
        index.parent.mkdir()
        index.write_text("".join(
            hashlib.sha256((self.runtime / name).read_bytes()).hexdigest() + "  " + name + "\n"
            for name in ("proton", "toolmanifest.vdf")
        ))

    def tearDown(self):
        self.temporary.cleanup()

    def test_install_preserves_proton_and_is_idempotent(self):
        original = (self.runtime / "proton").read_bytes()
        INSTALLER.install(self.runtime, HERE / "probe-wrapper.py")
        self.assertEqual((self.runtime / "proton").read_bytes(), original)
        self.assertIn('"commandline" "/probe-wrapper.py %verb%"', (self.runtime / "toolmanifest.vdf").read_text())
        index = self.runtime / "eso-bnet/RUNTIME-SHA256SUMS"
        first = index.read_bytes()
        for line in first.decode().splitlines():
            digest, name = line.split("  ", 1)
            self.assertEqual(hashlib.sha256((self.runtime / name).read_bytes()).hexdigest(), digest)
        INSTALLER.install(self.runtime, HERE / "probe-wrapper.py")
        self.assertEqual(index.read_bytes(), first)

    def test_tampered_runtime_is_rejected_before_writes(self):
        (self.runtime / "proton").write_text("unexpected change")
        original = (self.runtime / "toolmanifest.vdf").read_bytes()
        with self.assertRaises(ValueError):
            INSTALLER.install(self.runtime, HERE / "probe-wrapper.py")
        self.assertEqual((self.runtime / "toolmanifest.vdf").read_bytes(), original)
        self.assertFalse((self.runtime / "probe-wrapper.py").exists())

    def test_custom_entrypoint_is_rejected_before_writes(self):
        (self.runtime / "toolmanifest.vdf").write_text('"commandline" "/custom-script %verb%"')
        with self.assertRaises(ValueError):
            INSTALLER.install(self.runtime, HERE / "probe-wrapper.py")
        self.assertFalse((self.runtime / "probe-wrapper.py").exists())


if __name__ == "__main__":
    unittest.main()
