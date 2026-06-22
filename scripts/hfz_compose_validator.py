#!/usr/bin/env python3
"""HyperFocus Z0ne - Brain Compose Validator (thin wrapper -> _broski_hook_core).

Usage:
    python scripts/hfz_compose_validator.py docker-compose.hyper-brain.yml
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _broski_hook_core as core  # noqa: E402
import hooks_config as cfg  # noqa: E402

if __name__ == "__main__":
    sys.exit(core.run_compose_validator(label=cfg.LABEL, argv=sys.argv[1:]))
