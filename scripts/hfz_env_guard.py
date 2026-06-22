#!/usr/bin/env python3
"""HyperFocus Z0ne - Brain Env Guard (thin wrapper -> _broski_hook_core)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _broski_hook_core as core  # noqa: E402
import hooks_config as cfg  # noqa: E402

if __name__ == "__main__":
    sys.exit(core.run_env_guard(
        label=cfg.LABEL,
        required=cfg.ENV_REQUIRED,
        placeholders_extra=cfg.ENV_PLACEHOLDERS_EXTRA,
        env_files=cfg.ENV_FILES,
        strip_quotes=cfg.ENV_STRIP_QUOTES,
        mode=cfg.ENV_MODE,
    ))
