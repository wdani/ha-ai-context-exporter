HA AI Context Exporter is a helper tool for Home Assistant users who want to analyze and improve their system with the help of AI.

The tool collects relevant system context such as entities, areas, devices, automations and configuration structure and exports it in a structured format.

Sensitive-value masking for the compact entity export is best-effort only. The add-on masks selected evidenced patterns by default, but missed sensitive values can still happen.

Users must manually review exports before sharing them. The add-on option `allow_sensitive_values` defaults to `false`; setting it to `true` allows raw compact sensitive values at the user's own risk.

Please open an issue if you find unmasked sensitive values in the compact export.

The exported package can then be used for AI-assisted system analysis, troubleshooting, automation design or architecture improvements.
