from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOK_SCRIPT = REPO_ROOT / "AIFS" / "aifs_claude_hook.py"


def _run_hook(tool_name: str, file_path: str) -> dict:
    payload = json.dumps({"tool_name": tool_name, "tool_input": {"file_path": file_path}})
    result = subprocess.run(
        [sys.executable, str(HOOK_SCRIPT)],
        input=payload,
        capture_output=True,
        text=True,
        timeout=15,
    )
    return json.loads(result.stdout)


def test_no_contract_folder_allows_create():
    target = str(REPO_ROOT / "AIFS" / "_hook_test" / "no_contract_probe.md")
    resp = _run_hook("Write", target)
    assert resp["hookSpecificOutput"]["permissionDecision"] == "allow"
    assert resp["hookSpecificOutput"]["hookEventName"] == "PreToolUse"


def test_ext_restricted_folder_blocks_non_md_create():
    target = str(REPO_ROOT / "AIFS" / "_hook_test" / "ext-restricted" / "probe.py")
    resp = _run_hook("Write", target)
    assert resp["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert resp["hookSpecificOutput"]["hookEventName"] == "PreToolUse"
    assert "create" in resp["systemMessage"].lower()
    assert "create" in resp["hookSpecificOutput"]["permissionDecisionReason"].lower()


def test_ext_restricted_folder_allows_md_create():
    target = str(REPO_ROOT / "AIFS" / "_hook_test" / "ext-restricted" / "probe.md")
    resp = _run_hook("Write", target)
    assert resp["hookSpecificOutput"]["permissionDecision"] == "allow"
    assert resp["hookSpecificOutput"]["hookEventName"] == "PreToolUse"


def test_ailock_pattern_blocks_regardless_of_extension():
    target = str(REPO_ROOT / "AIFS" / "_hook_test" / "ailock-guarded" / "secret.md")
    resp = _run_hook("Write", target)
    assert resp["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert resp["hookSpecificOutput"]["hookEventName"] == "PreToolUse"
    assert "ailock" in resp["systemMessage"].lower()
    assert "ailock" in resp["hookSpecificOutput"]["permissionDecisionReason"].lower()


def test_trust_tier_edit_only_blocks_create():
    target = str(REPO_ROOT / "AIFS" / "_hook_test" / "trust-tier" / "new_file.md")
    resp = _run_hook("Write", target)
    assert resp["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert resp["hookSpecificOutput"]["hookEventName"] == "PreToolUse"
    assert "edit_only" in resp["systemMessage"].lower()
    assert "edit_only" in resp["hookSpecificOutput"]["permissionDecisionReason"].lower()


def test_trust_tier_edit_only_allows_edit_of_existing_file():
    existing = REPO_ROOT / "AIFS" / "_hook_test" / "trust-tier" / "existing.md"
    existing.parent.mkdir(parents=True, exist_ok=True)
    existing.write_text("pilot fixture\n", encoding="utf-8")
    resp = _run_hook("Edit", str(existing))
    assert resp["hookSpecificOutput"]["permissionDecision"] == "allow"
    assert resp["hookSpecificOutput"]["hookEventName"] == "PreToolUse"


def test_path_outside_repo_root_allows():
    resp = _run_hook("Write", "C:/Windows/Temp/outside_repo_probe.md")
    assert resp["hookSpecificOutput"]["permissionDecision"] == "allow"
    assert resp["hookSpecificOutput"]["hookEventName"] == "PreToolUse"


def test_non_write_edit_tool_allows_without_checking_contract():
    target = str(REPO_ROOT / "AIFS" / "_hook_test" / "ext-restricted" / "probe.py")
    resp = _run_hook("Read", target)
    assert resp["hookSpecificOutput"]["permissionDecision"] == "allow"
    assert resp["hookSpecificOutput"]["hookEventName"] == "PreToolUse"


def test_malformed_stdin_fails_open():
    result = subprocess.run(
        [sys.executable, str(HOOK_SCRIPT)],
        input="not valid json",
        capture_output=True,
        text=True,
        timeout=15,
    )
    resp = json.loads(result.stdout)
    assert resp["hookSpecificOutput"]["permissionDecision"] == "allow"
    assert resp["hookSpecificOutput"]["hookEventName"] == "PreToolUse"
    assert "error" in resp["systemMessage"].lower()


def test_changelog_gets_a_line_for_each_decision():
    changelog = REPO_ROOT / "AIFS" / "_hook_test" / "ext-restricted" / "CHANGELOG.ai.md"
    if changelog.exists():
        changelog.unlink()
    _run_hook("Write", str(REPO_ROOT / "AIFS" / "_hook_test" / "ext-restricted" / "probe.py"))
    assert changelog.exists()
    content = changelog.read_text(encoding="utf-8")
    assert "BLOCK" in content


def test_aifs_watcher_import_failure_fails_open():
    """Regression test for a Critical review finding: `from aifs_watcher import
    ...` must never be reachable outside main()'s try/except. Forces a real
    ImportError by temporarily hiding aifs_watcher.py (the module the hook
    depends on) so `import aifs_watcher` fails inside the subprocess, then
    asserts the hook still emits clean fail-open JSON instead of crashing
    with an uncaught traceback / non-zero exit / empty stdout.
    """
    watcher = REPO_ROOT / "AIFS" / "aifs_watcher.py"
    hidden = REPO_ROOT / "AIFS" / "aifs_watcher.py.hidden_for_test"
    assert watcher.exists(), "aifs_watcher.py must exist before this test can hide it"
    watcher.rename(hidden)
    try:
        target = str(REPO_ROOT / "AIFS" / "_hook_test" / "import_failure_probe.md")
        payload = json.dumps({"tool_name": "Write", "tool_input": {"file_path": target}})
        result = subprocess.run(
            [sys.executable, str(HOOK_SCRIPT)],
            input=payload,
            capture_output=True,
            text=True,
            timeout=15,
        )
    finally:
        hidden.rename(watcher)

    assert result.returncode == 0
    resp = json.loads(result.stdout)
    assert resp["hookSpecificOutput"]["permissionDecision"] == "allow"
    assert resp["hookSpecificOutput"]["hookEventName"] == "PreToolUse"
    assert "error" in resp["systemMessage"].lower()
