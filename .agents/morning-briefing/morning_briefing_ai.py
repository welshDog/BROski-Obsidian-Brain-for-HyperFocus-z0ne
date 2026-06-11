#!/usr/bin/env python3
"""
morning_briefing_ai.py
Generates AI-enhanced morning briefings with predictive prioritization.
Uses vault context + MCP + heuristics to build the perfect daily start.
BROski♾️
"""

import asyncio
import json
import os
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List

import aiofiles


class MorningBriefingAI:
    """Generates intelligent morning briefings for neurodivergent brains."""

    def __init__(self, vault_path: str, mcp_bridge=None):
        self.vault_path = vault_path
        self.mcp = mcp_bridge
        self.briefings_dir = os.path.join(vault_path, "00-Inbox", "Briefings")

    async def generate(self, date: str = None, include_ai: bool = True,
                      include_forecast: bool = True) -> Dict[str, Any]:
        """Generate comprehensive morning briefing."""
        target_date = date or datetime.utcnow().strftime("%Y-%m-%d")

        # 1. Yesterday's wins
        yesterday_wins = await self._get_yesterday_wins()

        # 2. Active projects + overdue tasks
        active_projects = await self._get_active_projects()
        overdue = await self._get_overdue_tasks()

        # 3. GitHub issues (recent)
        github_issues = await self._get_recent_github_issues()

        # 4. Streak status
        streak = await self._get_streak_data()

        # 5. Focus forecast (if enabled)
        forecast = await self._generate_focus_forecast() if include_forecast else None

        # 6. AI suggestions (if MCP available)
        ai_suggestions = None
        if include_ai and self.mcp and self.mcp.connected:
            ai_suggestions = await self._get_ai_prioritization(
                active_projects, overdue, yesterday_wins
            )

        briefing = {
            "date": target_date,
            "generated_at": datetime.utcnow().isoformat(),
            "yesterday_wins": yesterday_wins,
            "active_projects": active_projects,
            "overdue_tasks": overdue,
            "github_issues": github_issues,
            "streak": streak,
            "focus_forecast": forecast,
            "ai_suggestions": ai_suggestions,
            "top_3": self._calculate_top_3(active_projects, overdue, ai_suggestions)
        }

        return briefing

    async def write_to_vault(self, briefing: Dict[str, Any], vault_path: str) -> str:
        """Write briefing as daily note."""
        os.makedirs(self.briefings_dir, exist_ok=True)

        fname = f"Briefing_{briefing['date']}.md"
        fpath = os.path.join(self.briefings_dir, fname)

        # Format sections
        wins_list = "\n".join(f"- 🎉 {w}" for w in briefing["yesterday_wins"][:5])
        projects_list = "\n".join(
            f"- [{'x' if p.get('status') == 'done' else ' '}] [[{p['name']}]] — {p.get('next_action', 'TBD')}"
            for p in briefing["active_projects"][:8]
        )
        overdue_list = "\n".join(
            f"- ⚠️ [[{t['file']}]] — {t['task'][:60]}"
            for t in briefing["overdue_tasks"][:5]
        ) if briefing["overdue_tasks"] else "✅ Nothing overdue!"

        issues_list = "\n".join(
            f"- 🐛 {i['repo']} #{i['number']}: {i['title'][:50]}"
            for i in briefing["github_issues"][:5]
        ) if briefing["github_issues"] else "✅ No urgent issues"

        top3 = briefing["top_3"]
        top3_list = "\n".join(f"{i+1}. {t}" for i, t in enumerate(top3))

        forecast_section = ""
        if briefing["focus_forecast"]:
            f = briefing["focus_forecast"]
            forecast_section = f"""
## 🔮 Focus Forecast
**Best window**: {f['best_window']}  
**Predicted flow**: {f['predicted_flow']}/10  
**Recommended difficulty**: {f['recommended_difficulty']}  
**Avoid**: {f['avoid']}
"""

        ai_section = ""
        if briefing["ai_suggestions"]:
            s = briefing["ai_suggestions"]
            cited = "\n".join(
                f"- 📎 [[{os.path.splitext(os.path.basename(p))[0]}]]"
                for p in s.get("sources", [])[:5]
            )
            cited_section = f"\n**Grounded in**:\n{cited}\n" if cited else ""
            skills = " · ".join(
                sk.removeprefix("skill:") for sk in s.get("skills", [])[:5]
            )
            skills_section = f"\n**Linked skills**: 🦸 {skills}\n" if skills else ""
            ai_section = f"""
## 🤖 AI Prioritization
{s['reasoning']}

**Suggested order**:
{chr(10).join(f"- {a}" for a in s['actions'])}
{cited_section}{skills_section}"""

        note = f"""---
created: {briefing['generated_at']}
date: {briefing['date']}
type: morning-briefing
tags: [briefing, daily, ai-generated]
---
# 🌅 Morning Briefing — {briefing['date']}

> *"Start small. Start now. The rest follows."*

---

## 🎯 Top 3 Today
{top3_list}

---

## 🎉 Yesterday's Wins
{wins_list}

---

## 🏗️ Active Projects
{projects_list}

---

## ⚠️ Overdue Tasks
{overdue_list}

---

## 🐛 GitHub Issues
{issues_list}

---

## 🔥 Streak Status
**Current**: {briefing['streak']['current_streak']} days 🔥  
**Longest**: {briefing['streak']['longest_streak']} days 🏆  
**Recovery tokens**: {briefing['streak']['recovery_tokens']} 🎟️

{forecast_section}
{ai_section}

---

## 🚀 Quick Start
1. ☕ Coffee + 5-min breathe
2. 🎯 Pick ONE from Top 3
3. ⏱️ Set 15-min timer
4. 🔥 GO — no overthinking

---
*Generated by THE HYPER BRAIN Morning Briefing AI*
"""
        async with aiofiles.open(fpath, "w", encoding="utf-8") as f:
            await f.write(note)
        return fpath

    async def _get_yesterday_wins(self) -> List[str]:
        """Find completed tasks from yesterday."""
        yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
        wins = []

        # Check archive and projects for yesterday's completions
        for root, dirs, fnames in os.walk(self.vault_path):
            dirs[:] = [d for d in dirs if d not in [".obsidian", "node_modules"]]
            for fname in fnames:
                if not fname.endswith(".md"):
                    continue
                fpath = os.path.join(root, fname)
                try:
                    mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
                    if mtime.strftime("%Y-%m-%d") == yesterday:
                        with open(fpath, "r", encoding="utf-8") as f:
                            content = f.read()
                        if "status: done" in content or "- [x]" in content:
                            rel = os.path.relpath(fpath, self.vault_path)
                            wins.append(rel)
                except:
                    pass

        return wins[:10]

    async def _get_active_projects(self) -> List[Dict]:
        """Get projects from 01-Projects with status."""
        projects_dir = os.path.join(self.vault_path, "01-Projects")
        projects = []

        if not os.path.exists(projects_dir):
            return projects

        for fname in os.listdir(projects_dir):
            if not fname.endswith(".md"):
                continue
            fpath = os.path.join(projects_dir, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()

                # Extract status from YAML
                status_match = re.search(r"status:\s*(\w+)", content)
                status = status_match.group(1) if status_match else "active"

                if status != "done":
                    # Find first unchecked task as next action
                    task_match = re.search(r"- \[ \] (.+)", content)
                    next_action = task_match.group(1) if task_match else "Review project"

                    projects.append({
                        "name": fname.replace(".md", ""),
                        "status": status,
                        "next_action": next_action[:80]
                    })
            except:
                pass

        return projects

    async def _get_overdue_tasks(self) -> List[Dict]:
        """Find tasks with past due dates."""
        overdue = []
        today = datetime.utcnow().date()

        for root, dirs, fnames in os.walk(self.vault_path):
            dirs[:] = [d for d in dirs if d not in [".obsidian", "node_modules"]]
            for fname in fnames:
                if not fname.endswith(".md"):
                    continue
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Find tasks with due dates
                    for match in re.finditer(r"- \[ \] (.+?) 📅 (\d{4}-\d{2}-\d{2})", content):
                        task = match.group(1)
                        due = datetime.strptime(match.group(2), "%Y-%m-%d").date()
                        if due < today:
                            rel = os.path.relpath(fpath, self.vault_path)
                            overdue.append({"file": rel, "task": task, "due": match.group(2)})
                except:
                    pass

        return overdue[:10]

    async def _get_recent_github_issues(self) -> List[Dict]:
        """Read recent GitHub issues from inbox."""
        github_dir = os.path.join(self.vault_path, "00-Inbox", "GitHub")
        issues = []

        if not os.path.exists(github_dir):
            return issues

        for fname in sorted(os.listdir(github_dir), key=lambda x: os.path.getmtime(
            os.path.join(github_dir, x)), reverse=True)[:10]:
            if not fname.endswith(".md"):
                continue
            fpath = os.path.join(github_dir, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()

                # Extract from YAML frontmatter
                repo_match = re.search(r"repo:\s*(.+)", content)
                num_match = re.search(r"number:\s*(\d+)", content)
                title_match = re.search(r"# .+? — (.+)", content)

                issues.append({
                    "repo": repo_match.group(1).strip() if repo_match else "unknown",
                    "number": int(num_match.group(1)) if num_match else 0,
                    "title": title_match.group(1) if title_match else fname
                })
            except:
                pass

        return issues

    async def _get_streak_data(self) -> Dict[str, Any]:
        """Read streak data."""
        streak_file = os.path.join(self.vault_path, "07-Streaks-Achievements", "streak-data.json")
        if os.path.exists(streak_file):
            with open(streak_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"current_streak": 0, "longest_streak": 0, "recovery_tokens": 1}

    async def _generate_focus_forecast(self) -> Dict[str, Any]:
        """Predict optimal focus conditions for today."""
        hour = datetime.utcnow().hour

        # Simple heuristic based on time of day
        if 6 <= hour <= 10:
            return {
                "best_window": "Now — 11:00 (morning peak)",
                "predicted_flow": 8,
                "recommended_difficulty": "hard",
                "avoid": "Meetings, email, social media"
            }
        elif 10 <= hour <= 12:
            return {
                "best_window": "14:00 — 16:00 (post-lunch recovery)",
                "predicted_flow": 6,
                "recommended_difficulty": "medium",
                "avoid": "Complex architecture decisions"
            }
        elif 14 <= hour <= 16:
            return {
                "best_window": "17:00 — 19:00 (second wind)",
                "predicted_flow": 7,
                "recommended_difficulty": "medium",
                "avoid": "Starting new features"
            }
        else:
            return {
                "best_window": "Tomorrow 06:00 — 10:00",
                "predicted_flow": 5,
                "recommended_difficulty": "easy",
                "avoid": "Deep work — wind down instead"
            }

    async def _get_ai_prioritization(self, projects, overdue, wins) -> Dict[str, Any]:
        """Use MCP to get AI prioritization suggestions."""
        if not self.mcp:
            return None

        context = f"""Active projects: {len(projects)}
Overdue tasks: {len(overdue)}
Yesterday's wins: {len(wins)}

Projects: {', '.join(p['name'] for p in projects[:5])}
Overdue: {', '.join(o['task'][:30] for o in overdue[:3])}
"""

        query = f"""Given this context, suggest the top 3 priorities for today.
Consider: urgency, momentum from yesterday, and ADHD-friendly task sizing.
Return as numbered list with brief reasoning.\n\n{context}"""

        # skip_context=False → graph-aware RAG (Phase 3-5): budget-capped vault
        # context, so suggestions cite the real notes they were grounded in
        result = await self.mcp.query_vault(query, skip_context=False)
        answer = result.get("answer", "")
        sources = result.get("sources") or []

        # Phase 5 skill layer: graph-linked skills for the cited notes
        skills = []
        related_fn = getattr(self.mcp, "related_skills", None)
        if related_fn and sources:
            skills = await related_fn(sources[:3])

        # Parse numbered list
        actions = []
        for line in answer.split("\n"):
            if re.match(r"^\d+[.\)]\s", line.strip()):
                actions.append(line.strip())

        return {
            "reasoning": answer[:500],
            "actions": actions[:5],
            "sources": sources[:5],
            "skills": skills[:5]
        }

    def _calculate_top_3(self, projects, overdue, ai_suggestions) -> List[str]:
        """Calculate top 3 priorities from all signals."""
        top = []

        # 1. Most overdue task
        if overdue:
            top.append(f"🚨 {overdue[0]['task'][:60]} (overdue)")

        # 2. AI suggestion or next project action
        if ai_suggestions and ai_suggestions.get("actions"):
            top.append(f"🤖 {ai_suggestions['actions'][0]}")
        elif projects:
            top.append(f"🏗️ {projects[0]['next_action'][:60]} ({projects[0]['name']})")

        # 3. Smallest win available
        if projects:
            # Find project with shortest next action
            smallest = min(projects, key=lambda p: len(p.get("next_action", "")))
            top.append(f"⚡ {smallest['next_action'][:60]} (quick win)")

        return top[:3]


# ── HTTP server (FastAPI) ─────────────────────────────────────────────────────

if __name__ == "__main__":
    import httpx
    import uvicorn
    from fastapi import FastAPI
    from pydantic import BaseModel

    _MCP_URL = os.environ.get("MCP_BRIDGE_URL", "http://agent-mcp-bridge:3302")

    class RemoteMCPBridge:
        """HTTP adapter to agent-mcp-bridge (:3302) — same interface as MCPBridge."""

        def __init__(self, url: str):
            self._url = url
            self.connected = False

        async def probe(self) -> None:
            for attempt in range(6):
                try:
                    async with httpx.AsyncClient(timeout=3.0) as c:
                        r = await c.get(f"{self._url}/health")
                        if r.status_code == 200:
                            self.connected = True
                            return
                except Exception:
                    pass
                await asyncio.sleep(2)
            self.connected = False

        async def query_vault(self, query: str, context_files=None, skip_context: bool = False) -> dict:
            params: dict = {"query": query}
            if skip_context:
                params["skip_context"] = "true"
            try:
                # outlast the bridge's OLLAMA_TIMEOUT_S (180s) — cold model load
                # on CPU Ollama pushed graph-RAG calls past the old 90s budget
                async with httpx.AsyncClient(timeout=240.0) as c:
                    r = await c.post(
                        f"{self._url}/tools/call_mcp_tool",
                        params=params,
                    )
                    r.raise_for_status()
                    return r.json()
            except httpx.ConnectError as e:
                # bridge is down — mark offline so we skip AI on the next call too
                self.connected = False
                return {"answer": "", "sources": [], "mode": "error", "error": str(e)}
            except Exception as e:
                # timeout or LLM error — bridge still up, don't flip connected
                return {"answer": "", "sources": [], "mode": "error", "error": str(e)}

        async def related_skills(self, note_paths: list) -> list:
            """Graph skill layer (Phase 5): related_skills for cited vault notes."""
            skills: list = []
            try:
                async with httpx.AsyncClient(timeout=10.0) as c:
                    for p in note_paths:
                        stem = os.path.splitext(os.path.basename(p))[0]
                        r = await c.get(f"{self._url}/graph/related/note:{stem}")
                        if r.status_code != 200:
                            continue
                        for s in r.json().get("related_skills", []):
                            if s not in skills:
                                skills.append(s)
            except Exception:
                pass  # skills are garnish — never block the briefing
            return skills

    _mcp = RemoteMCPBridge(_MCP_URL)
    _briefing = MorningBriefingAI(
        vault_path=os.environ.get("OBSIDIAN_VAULT_PATH", "/vault"),
        mcp_bridge=_mcp,
    )

    _app = FastAPI(title="Morning Briefing Agent", version="0.2.0")

    @_app.on_event("startup")
    async def _startup():
        await _mcp.probe()
        print(f"MCP bridge {'connected ✅' if _mcp.connected else 'offline ⚠️'} → {_MCP_URL}")

    class GenerateRequest(BaseModel):
        date: str = None
        include_ai: bool = True       # AI suggestions via agent-mcp-bridge
        include_forecast: bool = True

    @_app.get("/health")
    async def _health():
        return {
            "status": "ok",
            "agent": "morning-briefing",
            "vault": _briefing.vault_path,
            "vault_exists": os.path.isdir(_briefing.vault_path),
            "mcp_bridge": {"url": _MCP_URL, "connected": _mcp.connected},
        }

    @_app.post("/generate")
    async def _generate(req: GenerateRequest = None):
        req = req or GenerateRequest()
        briefing = await _briefing.generate(
            date=req.date,
            include_ai=req.include_ai,
            include_forecast=req.include_forecast,
        )
        return {"status": "ok", "briefing": briefing}

    uvicorn.run(
        _app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 3304)),
    )
