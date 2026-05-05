"""HYPER BRAIN v3.0 — Session Snapshot & Recovery
Level 20 | State capture + recovery for interrupted hyperfocus sessions
"""
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List

VAULT_PATH = Path(os.environ.get("VAULT_PATH", "/vault"))
SNAPSHOTS_DIR = VAULT_PATH / "HYPERFOCUS_ZONE" / "Snapshots"


class SessionSnapshot:
    """Captures and restores hyperfocus session state."""

    def __init__(self):
        SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        self.current_snapshot: Optional[dict] = None

    def capture(self,
                task: str,
                context: str = "",
                open_files: Optional[List[str]] = None,
                mental_state: str = "focused",
                energy_level: int = 5,
                notes: str = "",
                tags: Optional[List[str]] = None) -> dict:
        """Capture the current session state."""
        snapshot = {
            "snapshot_id": f"snap_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "captured_at": datetime.now().isoformat(),
            "task": task,
            "context": context,
            "open_files": open_files or [],
            "mental_state": mental_state,
            "energy_level": energy_level,
            "notes": notes,
            "tags": tags or [],
            "recovery_prompt": self._generate_recovery_prompt(task, context, notes)
        }

        self.current_snapshot = snapshot
        self._save_snapshot(snapshot)
        return snapshot

    def _generate_recovery_prompt(self, task: str, context: str, notes: str) -> str:
        """Generate a re-entry prompt to resume focus quickly."""
        lines = [
            f"## 🧠 Resume: {task}",
            "",
            "**When you return, read this first:**",
        ]
        if context:
            lines.append(f"- Context: {context}")
        if notes:
            lines.append(f"- Where you left off: {notes}")
        lines.extend([
            "- Take 3 breaths",
            "- Re-read the last 5 lines of your work",
            "- Type one sentence to continue",
            "",
            "*You've got this. The brain is primed. Let's go BROski♾️!*"
        ])
        return "\n".join(lines)

    def _save_snapshot(self, snapshot: dict):
        filename = f"{snapshot['snapshot_id']}.json"
        filepath = SNAPSHOTS_DIR / filename
        filepath.write_text(json.dumps(snapshot, indent=2))

        # Also write a human-readable MD file
        md_file = SNAPSHOTS_DIR / f"{snapshot['snapshot_id']}.md"
        md_content = f"""# 📸 Session Snapshot

**Captured:** {snapshot['captured_at'][:16]}
**Task:** {snapshot['task']}
**Energy:** {snapshot['energy_level']}/10
**Mental State:** {snapshot['mental_state']}

## Context
{snapshot['context'] or 'No context captured'}

## Notes
{snapshot['notes'] or 'No notes'}

## Open Files
{chr(10).join(f'- {f}' for f in snapshot['open_files']) or 'None'}

{snapshot['recovery_prompt']}
"""
        md_file.write_text(md_content)
        print(f"📸 Snapshot saved: {snapshot['snapshot_id']}")

    def load_latest(self) -> Optional[dict]:
        snapshots = sorted(SNAPSHOTS_DIR.glob("snap_*.json"), reverse=True)
        if not snapshots:
            return None
        try:
            return json.loads(snapshots[0].read_text())
        except Exception:
            return None

    def restore(self) -> str:
        """Load latest snapshot and return recovery prompt."""
        snapshot = self.load_latest()
        if not snapshot:
            return "No snapshots found. Start a new session!"

        elapsed = (datetime.now() - datetime.fromisoformat(
            snapshot["captured_at"]
        )).seconds // 60

        return f"""# 🔄 Session Restored!

**Last task:** {snapshot['task']}
**Captured:** {elapsed} minutes ago
**Energy when paused:** {snapshot['energy_level']}/10

{snapshot['recovery_prompt']}
"""


if __name__ == "__main__":
    s = SessionSnapshot()
    snap = s.capture(
        task="Build HYPER BRAIN v3.0 engine scripts",
        context="Writing all 9 Python files for the 30th container",
        notes="Just finished mcp_bridge.py, next is morning_briefing_ai.py",
        energy_level=8,
        mental_state="hyperfocus"
    )
    print(f"📸 Captured: {snap['snapshot_id']}")
    print(s.restore())
