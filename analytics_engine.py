#!/usr/bin/env python3
"""
analytics_engine.py
Generates focus analytics, heatmaps, streak tracking, and BROski$ awards.
Writes Dataview-compatible YAML reports to vault.
BROski♾️
"""

import asyncio
import json
import os
import re
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Any, List

import aiofiles
import yaml


class AnalyticsEngine:
    def __init__(self, vault_path: str):
        self.vault_path = vault_path
        self.sessions_dir = os.path.join(vault_path, "05-Focus-Sessions")
        self.streaks_dir = os.path.join(vault_path, "07-Streaks-Achievements")
        self.analytics_dir = os.path.join(vault_path, "02-Areas", "Focus-Analytics")

    async def generate_weekly_report(self) -> Dict[str, Any]:
        """Analyze last 7 days of focus sessions."""
        sessions = await self._load_sessions(days=7)

        if not sessions:
            return {"message": "No sessions found. Start focusing!"}

        total_minutes = sum(s.get("actual_minutes", 0) for s in sessions)
        avg_flow = sum(s.get("flow_score", 0) for s in sessions) / len(sessions)
        avg_mood = sum(s.get("mood", 5) for s in sessions) / len(sessions)

        # Daily breakdown
        daily = defaultdict(lambda: {"minutes": 0, "sessions": 0, "flow": 0.0})
        for s in sessions:
            day = s.get("created", "")[:10]  # YYYY-MM-DD
            if day:
                daily[day]["minutes"] += s.get("actual_minutes", 0)
                daily[day]["sessions"] += 1
                daily[day]["flow"] += s.get("flow_score", 0)

        for d in daily:
            daily[d]["flow"] = round(daily[d]["flow"] / daily[d]["sessions"], 2)

        # Project breakdown
        projects = defaultdict(lambda: {"minutes": 0, "sessions": 0})
        for s in sessions:
            proj = s.get("project", "None") or "None"
            projects[proj]["minutes"] += s.get("actual_minutes", 0)
            projects[proj]["sessions"] += 1

        # Difficulty distribution
        difficulties = defaultdict(int)
        for s in sessions:
            difficulties[s.get("difficulty", "medium")] += 1

        # Best focus window
        hour_performance = defaultdict(lambda: {"flow": 0.0, "count": 0})
        for s in sessions:
            hour = int(s.get("created", "T00")[11:13]) if len(s.get("created", "")) > 13 else 0
            hour_performance[hour]["flow"] += s.get("flow_score", 0)
            hour_performance[hour]["count"] += 1

        best_hour = max(hour_performance, key=lambda h: hour_performance[h]["flow"] / max(1, hour_performance[h]["count"]))

        report = {
            "week_of": (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d"),
            "generated_at": datetime.utcnow().isoformat(),
            "total_sessions": len(sessions),
            "total_focus_minutes": total_minutes,
            "avg_flow_score": round(avg_flow, 2),
            "avg_mood": round(avg_mood, 1),
            "best_focus_hour": f"{best_hour:02d}:00",
            "daily_breakdown": dict(daily),
            "project_breakdown": dict(projects),
            "difficulty_distribution": dict(difficulties),
            "trend": "improving" if avg_flow > 0.6 else "steady" if avg_flow > 0.4 else "needs_attention"
        }

        return report

    async def write_to_vault(self, report: Dict[str, Any], vault_path: str) -> str:
        """Write weekly report as markdown with YAML frontmatter."""
        os.makedirs(self.analytics_dir, exist_ok=True)

        week_str = report.get("week_of", datetime.utcnow().strftime("%Y-W%U"))
        fname = f"Weekly-Report_{week_str}.md"
        fpath = os.path.join(self.analytics_dir, fname)

        # Convert to YAML frontmatter
        yaml_front = yaml.dump(report, default_flow_style=False, sort_keys=False)

        daily_rows = "\n".join(
            f"| {day} | {data['minutes']}m | {data['sessions']} | {data['flow']} |"
            for day, data in sorted(report.get("daily_breakdown", {}).items())
        )

        project_rows = "\n".join(
            f"| {proj} | {data['minutes']}m | {data['sessions']} |"
            for proj, data in sorted(report.get("project_breakdown", {}).items(), key=lambda x: -x[1]['minutes'])
        )

        note = f"""---
{yaml_front}---
# 📊 Weekly Focus Analytics — {week_str}

**Trend**: {report['trend'].upper()} {'📈' if report['trend'] == 'improving' else '➡️' if report['trend'] == 'steady' else '⚠️'}
**Total Focus Time**: {report['total_focus_minutes']} minutes across {report['total_sessions']} sessions
**Average Flow**: {"⭐" * int(report['avg_flow_score'] * 5)} ({report['avg_flow_score']})
**Best Focus Window**: 🕐 {report['best_focus_hour']}

## Daily Breakdown
| Day | Minutes | Sessions | Avg Flow |
|-----|---------|----------|----------|
{daily_rows}

## Project Distribution
| Project | Minutes | Sessions |
|---------|---------|----------|
{project_rows}

## Difficulty Distribution
```pie
{json.dumps(report.get('difficulty_distribution', {}), indent=2)}
```

---
*Generated by THE HYPER BRAIN Analytics Engine*
"""
        async with aiofiles.open(fpath, "w", encoding="utf-8") as f:
            await f.write(note)
        return fpath

    async def award_for_session(self, result: Dict[str, Any]) -> tuple:
        """Calculate BROski$ + XP for a completed session."""
        # Base awards
        diff_multipliers = {"easy": 1.0, "medium": 1.5, "hard": 2.5}
        mult = diff_multipliers.get(result.get("difficulty", "medium"), 1.5)

        base_coins = int(25 * mult)
        base_xp = int(15 * mult)

        # Flow bonus
        flow = result.get("flow_score", 0)
        flow_bonus_coins = int(flow * 50)
        flow_bonus_xp = int(flow * 30)

        # Mood bonus
        mood = result.get("mood", 5)
        mood_bonus = max(0, (mood - 5)) * 3

        total_coins = base_coins + flow_bonus_coins + mood_bonus
        total_xp = base_xp + flow_bonus_xp + mood_bonus

        return total_coins, total_xp

    async def update_streaks(self) -> Dict[str, Any]:
        """Track daily focus streaks with recovery token logic."""
        os.makedirs(self.streaks_dir, exist_ok=True)
        streak_file = os.path.join(self.streaks_dir, "streak-data.json")

        # Load existing
        data = {"current_streak": 0, "longest_streak": 0, "last_focus_date": None, "recovery_tokens": 1}
        if os.path.exists(streak_file):
            async with aiofiles.open(streak_file, "r", encoding="utf-8") as f:
                content = await f.read()
                if content:
                    data = json.loads(content)

        today = datetime.utcnow().strftime("%Y-%m-%d")
        yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")

        last = data.get("last_focus_date")

        if last == today:
            # Already focused today — streak holds
            pass
        elif last == yesterday:
            # Continued streak
            data["current_streak"] += 1
            data["last_focus_date"] = today
            if data["current_streak"] > data["longest_streak"]:
                data["longest_streak"] = data["current_streak"]
        else:
            # Streak broken — check recovery token
            if data.get("recovery_tokens", 0) > 0:
                data["recovery_tokens"] -= 1
                data["last_focus_date"] = today
                # Streak preserved via token
            else:
                data["current_streak"] = 1
                data["last_focus_date"] = today

        # Award recovery token every 7 days
        if data["current_streak"] > 0 and data["current_streak"] % 7 == 0:
            data["recovery_tokens"] = min(3, data.get("recovery_tokens", 0) + 1)

        async with aiofiles.open(streak_file, "w", encoding="utf-8") as f:
            await f.write(json.dumps(data, indent=2))

        return data

    async def get_streaks(self) -> Dict[str, Any]:
        streak_file = os.path.join(self.streaks_dir, "streak-data.json")
        if os.path.exists(streak_file):
            async with aiofiles.open(streak_file, "r", encoding="utf-8") as f:
                content = await f.read()
                return json.loads(content) if content else {"current_streak": 0, "recovery_tokens": 1}
        return {"current_streak": 0, "longest_streak": 0, "recovery_tokens": 1}

    async def generate_heatmap(self, days: int = 30) -> List[Dict]:
        """Generate focus intensity heatmap data."""
        sessions = await self._load_sessions(days=days)

        # Build day-hour matrix
        heatmap = defaultdict(lambda: {"minutes": 0, "flow_sum": 0.0, "count": 0})

        for s in sessions:
            created = s.get("created", "")
            if len(created) >= 13:
                day = created[:10]
                hour = int(created[11:13])
                key = f"{day}_{hour}"
                heatmap[key]["minutes"] += s.get("actual_minutes", 0)
                heatmap[key]["flow_sum"] += s.get("flow_score", 0)
                heatmap[key]["count"] += 1

        result = []
        for key, data in heatmap.items():
            day, hour = key.split("_")
            intensity = min(1.0, data["minutes"] / 60.0)  # Normalize to 1h = max
            result.append({
                "day": day,
                "hour": int(hour),
                "intensity": round(intensity, 2),
                "minutes": data["minutes"],
                "avg_flow": round(data["flow_sum"] / max(1, data["count"]), 2)
            })

        return sorted(result, key=lambda x: (x["day"], x["hour"]))

    async def _load_sessions(self, days: int = 7) -> List[Dict]:
        """Load session YAML frontmatter from 05-Focus-Sessions/."""
        sessions = []
        if not os.path.exists(self.sessions_dir):
            return sessions

        cutoff = datetime.utcnow() - timedelta(days=days)

        for fname in os.listdir(self.sessions_dir):
            if not fname.endswith(".md"):
                continue
            fpath = os.path.join(self.sessions_dir, fname)
            try:
                async with aiofiles.open(fpath, "r", encoding="utf-8") as f:
                    content = await f.read()

                # Extract YAML frontmatter
                match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
                if match:
                    front = yaml.safe_load(match.group(1))
                    created = front.get("created", "")
                    if created:
                        try:
                            dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                            if dt >= cutoff:
                                sessions.append(front)
                        except:
                            pass
            except Exception as e:
                print(f"⚠️ Error reading {fname}: {e}")

        return sessions
