#!/usr/bin/env python3
"""
session_snapshot.py
Captures and restores vault + brain state for ADHD context recovery.
Essential for: interruptions, hyperfocus crashes, day transitions.
BROski♾️
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any, List

import aiofiles


class SessionSnapshot:
    """Captures vault state for instant context recovery."""

    def __init__(self, vault_path: str, focus_tracker=None, distraction_filter=None):
        self.vault_path = vault_path
        self.snapshots_dir = os.path.join(vault_path, "06-AI-Context", "snapshots")
        self._focus_tracker = focus_tracker
        self._distraction_filter = distraction_filter

    async def capture(self, session_id: str) -> Dict[str, Any]:
        """Capture current vault state + open files + active thoughts."""
        snapshot_id = str(uuid.uuid4())[:8]
        timestamp = datetime.utcnow()

        # 1. Recently modified files (last 24h)
        recent_files = await self._get_recent_files(hours=24)

        # 2. Open / in-progress notes (files with status != done)
        active_notes = await self._get_active_notes()

        # 3. Current daily note content
        daily_note = await self._get_daily_note()

        # 4. Git status (uncommitted changes)
        git_status = await self._get_git_status()

        # 5. Focus session context
        focus_context = await self._get_focus_context()

        snapshot = {
            "id": snapshot_id,
            "session_id": session_id,
            "timestamp": timestamp.isoformat(),
            "recent_files": recent_files,
            "active_notes": active_notes,
            "daily_note_excerpt": daily_note[:500] if daily_note else "",
            "git_status": git_status,
            "focus_context": focus_context,
            "recovery_prompt": self._generate_recovery_prompt(
                recent_files, active_notes, focus_context
            )
        }

        return snapshot

    async def write_to_vault(self, snapshot: Dict[str, Any]):
        """Write snapshot as recoverable note."""
        os.makedirs(self.snapshots_dir, exist_ok=True)

        fname = f"Snapshot_{snapshot['id']}_{snapshot['timestamp'][:10]}.md"
        fpath = os.path.join(self.snapshots_dir, fname)

        recent_list = "\n".join(f"- [[{f['path']}]] (edited {f['ago']} ago)" 
                                  for f in snapshot["recent_files"][:10])
        active_list = "\n".join(f"- [[{n['path']}]] — {n['status']}" 
                                  for n in snapshot["active_notes"][:10])

        note = f"""---
created: {snapshot['timestamp']}
session_id: {snapshot['session_id']}
snapshot_id: {snapshot['id']}
type: snapshot
tags: [snapshot, context-recovery, ai-context]
---
# 🧠 Session Snapshot {snapshot['id']}

> **When to use**: You got interrupted. You crashed. It's tomorrow morning.
> **How**: Read the recovery prompt. Click the links. You're back.

---

## 🚀 Recovery Prompt

{snapshot['recovery_prompt']}

---

## 📁 Recent Files (Last 24h)
{recent_list}

## 🔄 Active Work
{active_list}

## 📝 Daily Note Excerpt
```
{snapshot['daily_note_excerpt'][:300]}...
```

## 🌿 Git Status
```
{snapshot['git_status']}
```

## 🎯 Focus Context
```json
{json.dumps(snapshot['focus_context'], indent=2)}
```

---
*Snapshot taken at {snapshot['timestamp']}*
*Restore your brain. One click at a time.*
"""
        async with aiofiles.open(fpath, "w", encoding="utf-8") as f:
            await f.write(note)

        print(f"📸 Snapshot saved: {fpath}")

    async def restore(self, snapshot_id: str) -> Dict[str, Any]:
        """Restore context from a snapshot."""
        # Find snapshot file
        for fname in os.listdir(self.snapshots_dir):
            if snapshot_id in fname:
                fpath = os.path.join(self.snapshots_dir, fname)
                async with aiofiles.open(fpath, "r", encoding="utf-8") as f:
                    content = await f.read()

                # Extract YAML frontmatter
                import re
                match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
                if match:
                    import yaml
                    data = yaml.safe_load(match.group(1))
                    return {
                        "restored": True,
                        "snapshot": data,
                        "message": f"🧠 Context restored from {snapshot_id}. Welcome back!",
                        "next_actions": [
                            f"Open daily note: [[{data.get('session_id', 'Daily')}]]",
                            "Review active notes above",
                            "Run Morning Briefing if it's a new day"
                        ]
                    }

        return {"restored": False, "error": "Snapshot not found"}

    async def _get_recent_files(self, hours: int = 24) -> List[Dict]:
        """Get recently modified markdown files."""
        import time
        cutoff = time.time() - (hours * 3600)
        files = []

        for root, dirs, fnames in os.walk(self.vault_path):
            dirs[:] = [d for d in dirs if d not in [".obsidian", "node_modules", "06-AI-Context"]]
            for fname in fnames:
                if not fname.endswith(".md"):
                    continue
                fpath = os.path.join(root, fname)
                mtime = os.path.getmtime(fpath)
                if mtime > cutoff:
                    rel = os.path.relpath(fpath, self.vault_path)
                    ago_min = int((time.time() - mtime) / 60)
                    ago_str = f"{ago_min}m" if ago_min < 60 else f"{ago_min//60}h"
                    files.append({"path": rel, "mtime": mtime, "ago": ago_str})

        files.sort(key=lambda x: -x["mtime"])
        return files

    async def _get_active_notes(self) -> List[Dict]:
        """Find notes with status != done."""
        active = []
        import re

        for root, dirs, fnames in os.walk(self.vault_path):
            dirs[:] = [d for d in dirs if d not in [".obsidian", "node_modules"]]
            for fname in fnames:
                if not fname.endswith(".md"):
                    continue
                fpath = os.path.join(root, fname)
                rel = os.path.relpath(fpath, self.vault_path)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        content = f.read()
                    # Check for status in YAML frontmatter
                    match = re.search(r"status:\s*(\w+)", content)
                    if match:
                        status = match.group(1)
                        if status not in ["done", "archived", "completed"]:
                            active.append({"path": rel, "status": status})
                except:
                    pass

        return active

    async def _get_daily_note(self) -> str:
        """Get today's daily note content."""
        today = datetime.utcnow().strftime("%Y-%m-%d")
        # Check common locations
        for loc in ["00-Inbox", "Daily", "Journal"]:
            fpath = os.path.join(self.vault_path, loc, f"{today}.md")
            if os.path.exists(fpath):
                with open(fpath, "r", encoding="utf-8") as f:
                    return f.read()
        return ""

    async def _get_git_status(self) -> str:
        """Get git status of vault."""
        import subprocess
        try:
            result = subprocess.run(
                ["git", "status", "--short"],
                cwd=self.vault_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout or "Clean working tree"
        except:
            return "Git not available"

    async def _get_focus_context(self) -> Dict[str, Any]:
        """Get current focus session context from live focus_tracker + distraction_filter."""
        if self._focus_tracker:
            status = await self._focus_tracker.get_current_status()
            ctx: Dict[str, Any] = {"active_session": status.get("active", False), **status}
            if self._distraction_filter and self._distraction_filter.active_session_id:
                ctx["distraction"] = await self._distraction_filter.get_recommendation()
            return ctx
        return {"active_session": False, "message": "No active session at snapshot time"}

    def _generate_recovery_prompt(self, recent: List[Dict], active: List[Dict], 
                                   focus: Dict) -> str:
        """Generate ADHD-friendly recovery instructions."""
        lines = ["### 🧭 Your Brain State"]

        if recent:
            lines.append(f"\n**Last touched**: [[{recent[0]['path']}]] ({recent[0]['ago']} ago)")

        if active:
            lines.append(f"\n**In progress**: {len(active)} notes")
            lines.append(f"→ Start here: [[{active[0]['path']}]]")

        lines.append("\n**Quick restart**:")
        lines.append("1. Read the last file you touched ☝️")
        lines.append("2. Check your daily note for today's intent")
        lines.append("3. Pick ONE micro-task. Set a 15-min timer.")
        lines.append("4. Go. Don't overthink. BROski's got you. ♾️")

        return "\n".join(lines)
