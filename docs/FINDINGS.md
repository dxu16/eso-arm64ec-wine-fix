# Findings behind the current recommendation

The original measured five-minute ESO self-exit was addressed by giving kernel32 imported entries the x64 Wine hotpatch prolog. That correction initially caused an ARM64EC native-call detour; recognizing the prolog in ntdll recovered the fast import-call path. Both corrections are retained in the BNet runtime with matching GE/BNet offsets and hashes.

Later stutter observations occurred during movement, while idle, and at the login screen. Add-on removal and a reduction from 36 to 30 FPS did not materially eliminate the large spikes, and they did not reliably coincide with the DXVK compiler indicator. The user found less stutter with the BNet variant than with the other compared bases. This motivates the current BNet recommendation without claiming a proven mechanism or universal fix.

BNet differs from its GE-Proton11-7 base in five built components: ARM64EC ntdll, two FEX translation DLLs, and their matching two Unix libraries. Both comparison variants used the same graphics base and the two ESO corrections. BNet's original Wine/FEX changes are retained as a matched set; this project did not add new FEX changes.

See [validation](VALIDATION.md), [upstream attribution](SOURCES-AND-LICENSES.md), and the [historical Valve investigation](legacy-valve/FINDINGS.md).
