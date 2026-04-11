# AI Change History

## Version 0.0.3
- Goal: fix add-on store schema/options parsing issue.
- Key changes: optional token schema retained, default removed (`options: {}`).
- Result: add-on config parse/build compatibility restored.
- Next focus: core-proxy-based authenticated read path.

## Version 0.0.4
- Goal: switch to official Core Proxy auth path.
- Key changes: `homeassistant_api: true`, core-proxy token-safe headers, `/api/ha-auth-debug`.
- Result: stable read-only proxy diagnostics and export flow.
- Next focus: semantics and discovery coverage improvements.

## Version 0.0.5
- Goal: improve discovery semantics and robustness.
- Key changes: explicit proxy API base, longer timeout, partial semantics for key categories.
- Result: more consistent export status evaluation and diagnostics.
- Next focus: ongoing discovery coverage and quality improvements.
