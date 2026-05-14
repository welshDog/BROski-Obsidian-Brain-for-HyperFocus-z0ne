from __future__ import annotations

import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import aiofiles
import yaml


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


async def _read_frontmatter(path: str) -> Optional[Dict[str, Any]]:
    try:
        async with aiofiles.open(path, "r", encoding="utf-8") as f:
            raw = await f.read()
    except FileNotFoundError:
        return None

    if not raw.startswith("---"):
        return None

    parts = raw.split("---", 2)
    if len(parts) < 3:
        return None

    fm_raw = parts[1].strip()
    if not fm_raw:
        return None

    data = yaml.safe_load(fm_raw)
    return data if isinstance(data, dict) else None


def _parse_created(value: Any) -> Optional[datetime]:
    if isinstance(value, datetime):
        dt = value
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    if not isinstance(value, str) or not value:
        return None

    v = value.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(v)
    except ValueError:
        return None

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


async def compute_gamification_summary(vault_path: str, level: int) -> Dict[str, Any]:
    streaks_dir = os.path.join(vault_path, "07-Streaks-Achievements")
    streaks_path = os.path.join(streaks_dir, "streak-data.json")

    streaks = {"current_streak": 0, "longest_streak": 0, "recovery_tokens": 1}
    try:
        async with aiofiles.open(streaks_path, "r", encoding="utf-8") as f:
            content = await f.read()
        if content:
            loaded = json.loads(content)
            if isinstance(loaded, dict):
                streaks.update({k: loaded.get(k, streaks[k]) for k in streaks})
    except FileNotFoundError:
        pass

    sessions_dir = os.path.join(vault_path, "05-Focus-Sessions")
    cutoff = _utcnow() - timedelta(days=7)

    coins_total = 0
    xp_total = 0
    sessions_count = 0

    if os.path.isdir(sessions_dir):
        for name in os.listdir(sessions_dir):
            if not name.lower().startswith("session_") or not name.lower().endswith(".md"):
                continue

            fm = await _read_frontmatter(os.path.join(sessions_dir, name))
            if not fm:
                continue

            created = _parse_created(fm.get("created"))
            if not created or created < cutoff:
                continue

            coins = fm.get("coins_earned", 0)
            xp = fm.get("xp_earned", 0)

            try:
                coins_total += int(coins)
            except (TypeError, ValueError):
                pass

            try:
                xp_total += int(xp)
            except (TypeError, ValueError):
                pass

            sessions_count += 1

    return {
        "level": int(level),
        "coins_total_7d": coins_total,
        "xp_total_7d": xp_total,
        "sessions_7d": sessions_count,
        "streaks": streaks,
        "generated_at": _utcnow().isoformat().replace("+00:00", "Z"),
    }
