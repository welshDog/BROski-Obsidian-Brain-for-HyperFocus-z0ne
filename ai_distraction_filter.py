#!/usr/bin/env python3
"""
ai_distraction_filter.py
AI-powered distraction filtering for ADHD brains.
Scores distractions by context, learns patterns, suggests interventions.
BROski♾️
"""

import asyncio
import json
import os
import re
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

import aiofiles


class DistractionFilter:
    """Learns user's distraction patterns and provides real-time filtering."""

    DISTRACTION_WEIGHTS = {
        "social_media": 0.95,
        "news": 0.80,
        "messaging": 0.70,
        "email": 0.60,
        "notification": 0.50,
        "internal": 0.40,  # self-interruption
        "app_switch": 0.30,
        "ambient_noise": 0.20
    }

    INTERVENTIONS = {
        "high": [
            "🛑 BLOCK: Close tab/app immediately",
            "🌬️ BREATHE: 4-7-8 breathing (4s in, 7s hold, 8s out)",
            "📝 DUMP: 30-second brain dump to inbox",
            "⏱️ RESET: 5-min micro-break, then return"
        ],
        "medium": [
            "⏳ DELAY: Write it down, handle in 25 min",
            "🎯 REFOCUS: Re-read your session intent aloud",
            "💧 HYDRATE: Drink water + stretch 30s"
        ],
        "low": [
            "✅ QUICK: If <2 min, do it now",
            "📌 PIN: Add to next break queue"
        ]
    }

    def __init__(self, vault_path: str):
        self.vault_path = vault_path
        self.active_session_id: Optional[str] = None
        self.distraction_log: List[Dict] = []
        self.patterns_file = os.path.join(vault_path, "02-Areas", "Focus-Analytics", "distraction-patterns.json")

    async def enable_for_session(self, session_id: str):
        self.active_session_id = session_id
        self.distraction_log = []

    async def disable_for_session(self, session_id: str):
        # Save session distractions
        if self.distraction_log:
            await self._save_session_distractions(session_id)
        self.active_session_id = None

    async def report(self, source: str, context: str, timestamp: Optional[datetime] = None) -> float:
        """Report a distraction. Returns severity score 0.0–1.0."""
        ts = timestamp or datetime.utcnow()

        # Calculate base score
        base_score = self.DISTRACTION_WEIGHTS.get(source, 0.50)

        # Context analysis
        context_boost = self._analyze_context(context)

        # Time-of-day modifier (ADHD peak distractibility)
        hour = ts.hour
        if 14 <= hour <= 16:  # Post-lunch crash
            base_score *= 1.2
        elif 20 <= hour <= 23:  # Evening fatigue
            base_score *= 1.1

        # Recent distraction frequency (cascading effect)
        recent_count = sum(1 for d in self.distraction_log 
                          if (ts - d["timestamp"]).total_seconds() < 300)
        cascade_boost = min(0.3, recent_count * 0.05)

        final_score = min(1.0, base_score + context_boost + cascade_boost)

        entry = {
            "timestamp": ts.isoformat(),
            "source": source,
            "context": context,
            "score": round(final_score, 2),
            "session_id": self.active_session_id
        }
        self.distraction_log.append(entry)

        return round(final_score, 2)

    async def get_recommendation(self) -> Dict[str, Any]:
        """Get intervention recommendation based on current state."""
        if not self.distraction_log:
            return {"level": "none", "message": "Focus strong. Keep going! 🔥"}

        recent_scores = [d["score"] for d in self.distraction_log[-5:]]
        avg_score = sum(recent_scores) / len(recent_scores)

        if avg_score > 0.7:
            level = "high"
        elif avg_score > 0.4:
            level = "medium"
        else:
            level = "low"

        return {
            "level": level,
            "avg_score": round(avg_score, 2),
            "interventions": self.INTERVENTIONS[level],
            "distractions_last_5min": len([d for d in self.distraction_log 
                                          if (datetime.utcnow() - datetime.fromisoformat(d["timestamp"])).total_seconds() < 300])
        }

    async def get_patterns(self, days: int = 7) -> Dict[str, Any]:
        """Analyze distraction patterns over time."""
        if not os.path.exists(self.patterns_file):
            return {"message": "Not enough data yet. Keep tracking!"}

        async with aiofiles.open(self.patterns_file, "r", encoding="utf-8") as f:
            content = await f.read()

        all_data = json.loads(content) if content else []
        cutoff = datetime.utcnow() - timedelta(days=days)

        recent = [d for d in all_data 
                 if datetime.fromisoformat(d["timestamp"]) >= cutoff]

        if not recent:
            return {"message": f"No distractions in last {days} days. Legend! 🏆"}

        # Source breakdown
        sources = defaultdict(lambda: {"count": 0, "avg_score": 0.0})
        for d in recent:
            src = d["source"]
            sources[src]["count"] += 1
            sources[src]["avg_score"] += d["score"]

        for src in sources:
            sources[src]["avg_score"] = round(sources[src]["avg_score"] / sources[src]["count"], 2)

        # Hourly heatmap
        hours = defaultdict(lambda: {"count": 0, "avg_score": 0.0})
        for d in recent:
            h = datetime.fromisoformat(d["timestamp"]).hour
            hours[h]["count"] += 1
            hours[h]["avg_score"] += d["score"]

        for h in hours:
            hours[h]["avg_score"] = round(hours[h]["avg_score"] / hours[h]["count"], 2)

        worst_hour = max(hours, key=lambda h: hours[h]["avg_score"])
        worst_source = max(sources, key=lambda s: sources[s]["avg_score"])

        return {
            "period_days": days,
            "total_distractions": len(recent),
            "avg_score": round(sum(d["score"] for d in recent) / len(recent), 2),
            "source_breakdown": dict(sources),
            "hourly_patterns": dict(hours),
            "worst_hour": f"{worst_hour:02d}:00",
            "worst_source": worst_source,
            "recommendations": self._generate_pattern_recommendations(dict(sources), dict(hours))
        }

    def _analyze_context(self, context: str) -> float:
        """Boost score based on urgency keywords in context."""
        urgency_keywords = ["urgent", "asap", "deadline", "boss", "client", "prod", "broken"]
        if any(k in context.lower() for k in urgency_keywords):
            return 0.15

        # FOMO keywords
        fomo_keywords = ["sale", "limited", "new", "trending", "viral", "drop"]
        if any(k in context.lower() for k in fomo_keywords):
            return 0.20

        return 0.0

    async def _save_session_distractions(self, session_id: str):
        """Persist distractions to pattern file."""
        os.makedirs(os.path.dirname(self.patterns_file), exist_ok=True)

        existing = []
        if os.path.exists(self.patterns_file):
            async with aiofiles.open(self.patterns_file, "r", encoding="utf-8") as f:
                content = await f.read()
                if content:
                    existing = json.loads(content)

        existing.extend(self.distraction_log)

        # Keep only last 90 days
        cutoff = datetime.utcnow() - timedelta(days=90)
        existing = [d for d in existing 
                   if datetime.fromisoformat(d["timestamp"]) >= cutoff]

        async with aiofiles.open(self.patterns_file, "w", encoding="utf-8") as f:
            await f.write(json.dumps(existing, indent=2))

    def _generate_pattern_recommendations(self, sources: Dict, hours: Dict) -> List[str]:
        """Generate personalized anti-distraction strategies."""
        recs = []

        if sources.get("social_media", {}).get("count", 0) > 5:
            recs.append("📵 Consider app blockers during focus hours (Cold Turkey, Freedom)")

        if sources.get("notification", {}).get("count", 0) > 3:
            recs.append("🔕 Enable Do Not Disturb + batch notifications to breaks")

        worst_hour = max(hours, key=lambda h: hours[h]["avg_score"]) if hours else 14
        recs.append(f"⚡ Your peak distractibility is {worst_hour:02d}:00 — schedule easy tasks then")

        if sources.get("internal", {}).get("count", 0) > 3:
            recs.append("🧠 High self-interruption — try body-doubling or focus music")

        return recs
