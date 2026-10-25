# Public-content boundaries

The public package contains the compiled Wine DLL, exact transformation, helper scripts, sanitized validation summaries, source pins, and upstream notices.

It must not contain credentials, SSH keys, private device backups, Steam account data, raw registries, game prefixes, process memory dumps, decrypted game code, resolved personal home-directory paths, or Python bytecode caches.

An audit of the initial repository found no authentication secrets, LAN addresses, or Steam account IDs. Unnecessary device paths were found in one environment record and inherited Python caches in the initial full-runtime archive. The environment record was removed from all published branch/tag history; the old release was deleted. The official overlay excludes those materials.

Upstream authors' public copyright/contact information is retained as required attribution. Automated scans and manual review do not prove the absence of every possible identifier. A Git history rewrite cannot erase external clones or all GitHub cached objects; GitHub Support controls server-side purging. [GitHub documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).

Run python3 scripts/check-public-content.py before publication. CI checks project files for credential shapes, private-key blocks, resolved user-home paths, and forbidden filenames. Private local backups are deliberately outside this repository.

## Ready-to-use archive

The full runtime is assembled from the official base and the public two-DLL overlay. Generated default prefixes, registries, caches, logs, locks, and local settings are excluded. Archive UID/GID, owner names and timestamps are canonicalized; symlinks cannot escape the tool. The packager scans file contents for credentials and the packaging account’s resolved home path. These checks complement review rather than proving the absence of every possible identifier. Source archives and upstream copyright/author notices are preserved as public upstream material.
