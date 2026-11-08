# Graphics probe isolation

Steam can run d3ddriverquery64.exe through multiple compatibility tools during startup. On the tested ARM64 setup, those invocations shared steamapps/compatdata/0. The journal recorded overlapping prefix upgrades between Proton builds, and BNet1's Windows DLLs were overwritten with files from another runtime. The ESO runtime's integrity check passed.

Proton locks prefix preparation, then releases that lock before executing Wine. Wine can subsequently update a prefix whose links and timestamp were changed by another probe. Its builtin DLL installer can overwrite a symlink target in the other runtime. A sandboxed control reproduced the automatic update and in-place target overwrite. Matching timestamps left the files intact, and ordinary prefix DLL copies confined updates to the prefix. The historical per-file writes were not individually audited.

## Runtime entry point

toolmanifest.vdf invokes probe-wrapper.py, which forwards normal launches to the original proton script. For an exact d3ddriverquery.exe or d3ddriverquery64.exe target, the wrapper uses a prefix under $XDG_CACHE_HOME/proton-graphics-probes, falling back to ~/.cache/proton-graphics-probes when that variable is unset or relative. The directory key includes the resolved runtime path, executable name, and DirectX 11 or DirectX 12 mode. Repeated invocations using the same key are locked for the Proton child process's lifetime. Signals are forwarded to that child.

This is an invocation wrapper with reusable prefix and lock files. It needs no background service and no game launch-option changes. Separate runtime directories receive separate probe prefixes even when Steam initially supplies the same compatdata/0 path.

## Existing runtime installation

Fully exit Steam and close applications using the tool. Verify the runtime against its own checksum index first. From this repository, run:

```sh
python3 -B bnet/install-probe-wrapper.py "$HOME/.local/share/Steam/compatibilitytools.d/GE-Proton11-7-ESO-BNet-arm64"
```

The helper adds the executable wrapper, changes only the tool manifest's standard /proton %verb% entry point, and refreshes an existing BNet or ESO runtime checksum index. It refuses checksum mismatches and unknown entry points before writing. Repeating the installation is supported. It also accepts other standard Proton tool directories through the same argument. Restart Steam afterward.

The complete v0.4.2 download already includes this entry point. Runtime replacement can remove a locally installed wrapper, so use a packaged version containing it or rerun the helper after verifying a replacement.

## Verification and cleanup

```sh
python3 -B bnet/test_probe_wrapper.py -v
```

Tests cover exact target matching, original arguments and environment, exit status, runtime/API/architecture separation, concurrent invocations, child-lifetime locking, signal forwarding, installer idempotence, and refusal of damaged runtime indexes. They run through scripts/verify.py in the existing GitHub Actions verification job.

With Steam and its probes closed, the proton-graphics-probes cache directory can be removed. It is recreated on demand. Retain the installed wrapper and its manifest entry point.

## Source

- [Pinned Wine DLL replacement code](https://github.com/ValveSoftware/wine/blob/e60892c/dlls/setupapi/fakedll.c#L569)
- [Pinned Wine automatic prefix update](https://github.com/ValveSoftware/wine/blob/e60892c/programs/wineboot/wineboot.c#L1659)
