import json
from pathlib import Path

import pytest

from gamification_summary import compute_gamification_summary


@pytest.mark.asyncio
async def test_compute_gamification_summary_rolls_up_frontmatter(tmp_path: Path):
    vault = tmp_path / "vault"
    sessions = vault / "05-Focus-Sessions"
    streaks_dir = vault / "07-Streaks-Achievements"
    sessions.mkdir(parents=True)
    streaks_dir.mkdir(parents=True)

    (streaks_dir / "streak-data.json").write_text(
        json.dumps({"current_streak": 2, "longest_streak": 5, "recovery_tokens": 1}),
        encoding="utf-8",
    )

    (sessions / "Session_abc_2026-05-14.md").write_text(
        """---
created: 2026-05-14T10:00:00Z
coins_earned: 25
xp_earned: 15
---
# Session
""",
        encoding="utf-8",
    )

    (sessions / "Session_def_2026-05-13.md").write_text(
        """---
created: 2026-05-13T10:00:00Z
coins_earned: 10
xp_earned: 5
---
# Session
""",
        encoding="utf-8",
    )

    summary = await compute_gamification_summary(str(vault), level=20)
    assert summary["level"] == 20
    assert summary["coins_total_7d"] == 35
    assert summary["xp_total_7d"] == 20
    assert summary["sessions_7d"] == 2
    assert summary["streaks"]["current_streak"] == 2
