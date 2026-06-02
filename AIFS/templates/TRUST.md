# TRUST.md
# Per-agent trust tiers for this folder.
# Unknown agents default to READ_ONLY.

## Trust Levels
- claude-3.5-sonnet: FULL
- github-copilot: EDIT_ONLY
- cursor: EDIT_ONLY
- windsurf: EDIT_ONLY
- unknown: READ_ONLY

## Trust Definitions
- FULL: All permissions per manifest.toml
- EDIT_ONLY: May edit existing files. May NOT create or delete.
- READ_ONLY: May read only. Zero writes.
- BLOCKED: No access at all. Hard stop.
