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
from typing import Any, Dict, Optional

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


# ── Level 19 — Dynamic XP (quality × chunk-difficulty × intensity) ──────────────
#
# The flat per-intensity multiplier (DIAL) is the BASE. The dynamic multiplier
# scales that base by how WELL the session went (quality_score) and how HARD the
# work was (chunk_difficulty from HyperSplit / Level 17). All pure + testable.


def session_quality_score(
    actual_minutes: int,
    estimated_minutes: int,
    distraction_avg: float = 0.0,
    mood: Optional[int] = None,
) -> float:
    """Score a focus session 0.0–1.0.

    - completion: how close actual time landed to the plan (over-runs don't punish).
    - focus: 1 - average distraction severity (0–1) over the session.
    - mood: optional 1–10 self-report, light bonus.
    """
    est = max(1, int(estimated_minutes or 1))
    act = max(0, int(actual_minutes or 0))
    completion = min(1.0, act / est)
    focus = max(0.0, 1.0 - max(0.0, min(1.0, float(distraction_avg))))
    if mood is not None:
        mood_factor = max(0.0, min(1.0, (float(mood) - 1) / 9))  # 1→0, 10→1
        score = 0.45 * completion + 0.40 * focus + 0.15 * mood_factor
    else:
        score = 0.55 * completion + 0.45 * focus
    return round(max(0.0, min(1.0, score)), 3)


def dynamic_multiplier(
    intensity: str,
    quality: float,
    chunk_difficulty: float = 0.5,
) -> float:
    """Final XP multiplier = base(intensity) × quality-band × difficulty-band.

    quality 0–1 → band 0.5–1.5 (a perfect session is worth 50% more than the
    base; a poor one half). chunk_difficulty 0–1 → band 0.8–1.4 (harder chunks
    pay more). Result is clamped to a sane 0.25–4.0 range.
    """
    base = DIAL.get(intensity, DIAL[DEFAULT])["xp_multiplier"]
    q = max(0.0, min(1.0, float(quality)))
    d = max(0.0, min(1.0, float(chunk_difficulty)))
    quality_band = 0.5 + q                 # 0.5 .. 1.5
    difficulty_band = 0.8 + 0.6 * d        # 0.8 .. 1.4
    mult = base * quality_band * difficulty_band
    return round(max(0.25, min(4.0, mult)), 3)
