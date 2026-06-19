"""P2-3 — Brain Level 18 (distraction monitor) + Level 19 (dynamic XP) unit tests.

Pure-logic only: signal evaluation + multiplier math + chunk-difficulty scoring.
No files, Redis, or Discord — those are exercised by the live :8100 engine.
"""

import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from distraction_monitor import evaluate_signals  # noqa: E402
from difficulty_dial import session_quality_score, dynamic_multiplier  # noqa: E402
from hyper_split import HyperSplitEngine  # noqa: E402


# ── Level 18 — signal evaluation ────────────────────────────────────────────────

def _files(*specs):
    """specs: (path, minutes_ago) -> recent_files list."""
    now = time.time()
    return [{"path": p, "mtime": now - m * 60} for p, m in specs]


def test_idle_signal_fires_after_15min():
    out = evaluate_signals(_files(("01-Projects/api.md", 20)), "build the api", now=time.time())
    assert out["signals"]["idle"]["idle"] is True
    assert any("idle" in c for _, c in out["reports"])


def test_no_idle_when_recent_edit():
    out = evaluate_signals(_files(("01-Projects/api.md", 2)), "build the api", now=time.time())
    assert out["signals"]["idle"]["idle"] is False


def test_rapid_switching_fires():
    files = _files(
        ("a.md", 1), ("b.md", 2), ("c.md", 3), ("d.md", 4), ("e.md", 5)
    )
    out = evaluate_signals(files, "writing a.md", now=time.time())
    assert out["signals"]["note_activity"]["rapid_switching"] is True


def test_topic_drift_detected():
    # intent is about "database migration"; most recent edit is an unrelated note.
    out = evaluate_signals(_files(("04-Archive/random_youtube_idea.md", 1)),
                           "database migration schema", now=time.time())
    assert out["signals"]["topic_drift"]["drift"] is True
    assert any("drift" in c for _, c in out["reports"])


def test_no_drift_when_on_topic():
    out = evaluate_signals(_files(("01-Projects/database_migration.md", 1)),
                           "database migration schema", now=time.time())
    assert out["signals"]["topic_drift"]["drift"] is False


def test_no_signals_clean_session():
    out = evaluate_signals(_files(("01-Projects/api_build.md", 1)), "api build", now=time.time())
    assert out["any_fired"] is False


# ── Level 19 — quality score + dynamic multiplier ───────────────────────────────

def test_quality_perfect_session():
    # completed the plan, zero distractions, great mood -> near 1.0
    q = session_quality_score(actual_minutes=25, estimated_minutes=25, distraction_avg=0.0, mood=10)
    assert q > 0.9


def test_quality_poor_session():
    # barely worked, heavy distractions, low mood -> low
    q = session_quality_score(actual_minutes=3, estimated_minutes=25, distraction_avg=0.9, mood=2)
    assert q < 0.3


def test_dynamic_multiplier_scales_with_quality_and_difficulty():
    base_low = dynamic_multiplier("medium", quality=0.2, chunk_difficulty=0.2)
    base_high = dynamic_multiplier("medium", quality=1.0, chunk_difficulty=1.0)
    assert base_high > base_low
    # medium base is 1.0; a perfect hard session should beat it, a poor easy one should be under.
    assert base_high > 1.0 > base_low


def test_dynamic_multiplier_respects_intensity():
    hyper = dynamic_multiplier("hyper", quality=0.8, chunk_difficulty=0.6)
    low = dynamic_multiplier("low", quality=0.8, chunk_difficulty=0.6)
    assert hyper > low  # higher intensity = higher base


def test_multiplier_clamped():
    assert 0.25 <= dynamic_multiplier("low", 0.0, 0.0) <= 4.0
    assert 0.25 <= dynamic_multiplier("chaos", 1.0, 1.0) <= 4.0


# ── Level 17 → 19 — HyperSplit chunk difficulty ─────────────────────────────────

def test_difficulty_score_harder_tree_scores_higher():
    easy = {"count": 3, "depth": 1, "estimated_total_minutes": 30}
    hard = {"count": 22, "depth": 3, "estimated_total_minutes": 170}
    assert HyperSplitEngine.difficulty_score(hard) > HyperSplitEngine.difficulty_score(easy)
    assert 0.0 <= HyperSplitEngine.difficulty_score(easy) <= 1.0
    assert 0.0 <= HyperSplitEngine.difficulty_score(hard) <= 1.0


def test_difficulty_score_empty_tree():
    assert HyperSplitEngine.difficulty_score({}) == 0.0
