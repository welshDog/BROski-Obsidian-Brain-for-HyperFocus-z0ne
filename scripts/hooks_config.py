#!/usr/bin/env python3
"""HyperFocus Z0ne - per-repo hook config for BROski-Obsidian-Brain.

Consumed by the thin hook wrappers, which call _broski_hook_core.run_*().
hfz_session_start stays bespoke (repo-specific checks).
"""

LABEL = "Brain"

# env_guard
ENV_REQUIRED = ["OBSIDIAN_VAULT_PATH", "GITHUB_WEBHOOK_SECRET", "GITHUB_PAT", "OLLAMA_MODEL"]
ENV_PLACEHOLDERS_EXTRA: list[str] = []
ENV_FILES = [".env"]
ENV_STRIP_QUOTES = False
ENV_MODE = "fail"

# broski_xp_reward
XP_CHANNEL = "broski_economy"
XP_DB = 1
XP_SOURCE = "brain_hook"
