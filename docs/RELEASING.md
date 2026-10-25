# Publishing the official-base release

Repository: https://github.com/dxu16/eso-arm64ec-wine-fix
Current tag: v0.3.0-experimental. The earlier BNet release was deleted; its scrubbed source tag remains as history.

1. Verify the exact DLL transformation and helper behavior.
2. Run python3 scripts/check-public-content.py and python3 scripts/verify.py.
3. Fetch the pinned Wine and Proton source archives with scripts/fetch-sources.py.
4. Build the precompiled overlay with scripts/package-overlay.py.
5. Record the three outer archive hashes/sizes in release-manifest.json and release-assets/SHA256SUMS; regenerate repository SHA256SUMS.
6. Upload the overlay, both source archives, SHA256SUMS, and release-manifest.json into a draft.
7. Verify GitHub's server asset digests, ensure CI passes, then publish as an experimental prerelease. Always explicitly preserve tag_name when updating the draft.

Large source/download archives stay in GitHub Releases, not Git history. Do not upload an entire device runtime or Wine prefix. The overlay contains precompiled output and an installer, not a recompilation of Wine. An equivalent ntdll source patch is included but was not compiled into the shipped DLL.
