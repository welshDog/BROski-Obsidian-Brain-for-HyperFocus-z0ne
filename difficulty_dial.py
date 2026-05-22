#!/usr/bin/env python3
"""
difficulty_dial.py
THE HYPER BRAIN v3.0 — Level 19

The DifficultyDial: a user-selectable focus intensity that scales XP rewards
and distraction-filter sensitivity. Persisted to a dedicated JSON file in the
vault (a dedicated file — never clobbers other config).
BROski♾️
"""

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict

import aiofiles

# intensity -> XP multiplier + distraction-filter sensitivity (0-1) + label
DIAL: Dict[str, Dict[str, Any]] = {
    "low":    {"xp_multiplier": 0.5, "sensitivity": 0.4, "label": "🌙 Low — gentle, low-stakes"},
    "medium": {"xp_multiplier": 1.0, "sensitivity": 0.6, "label": "⚡ Medium — standard focus"},
    "hyper":  {"xp_multiplier": 1.5, "sensitivity": 0.8, "label": "🔥 Hyper — locked in"},
    "chaos":  {"xp_multiplier": 2.0, "sensitivity": 1.0, "label": "🌀 Chaos — maximum stakes"},
}
DEFAULT = "medium"


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class DifficultyDial:
    """Reads/writes the focus-intensity preference and exposes its effects."""

    def __init__(self, vault_path: str):
        self.vault_path = vault_path
        self.path = os.path.join(vault_path, "03-Resources", "difficulty-dial.json")

    async def get(self) -> Dict[str, Any]:
        intensity = await self._read()
        return {"intensity": intensity, **DIAL[intensity]}

    async def set(self, intensity: str) -> Dict[str, Any]:
        key = (intensity or "").strip().lower()
        if key not in DIAL:
            raise ValueError(
                f"Unknown intensity '{intensity}'. Choose one of: {', '.join(DIAL)}"
            )
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        record = {"intensity": key, "updated": _utcnow_iso(), **DIAL[key]}
        async with aiofiles.open(self.path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(record, indent=2))
        return {**record, "saved": True}

    def multiplier(self, intensity: str) -> float:
        """XP multiplier for an intensity — safe for unknown values."""
        return DIAL.get(intensity, DIAL[DEFAULT])["xp_multiplier"]

    async def _read(self) -> str:
        try:
            async with aiofiles.open(self.path, "r", encoding="utf-8") as f:
                data = json.loads(await f.read())
            value = str(data.get("intensity", DEFAULT)).lower()
            return value if value in DIAL else DEFAULT
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            return DEFAULT
