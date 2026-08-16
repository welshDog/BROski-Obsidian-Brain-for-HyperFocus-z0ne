# AIFS Claude Code Enforcement Hook Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A `PreToolUse` hook that makes AIFS folder contracts genuinely preventive for Claude Code `Write`/`Edit` calls in this repo — real `allow`/`deny`/`ask` decisions before a write happens, not just an after-the-fact log entry.

**Architecture:** New script `AIFS/aifs_claude_hook.py` reuses `aifs_watcher.py`'s existing `ContractResolver`/`AIFSEnforcer`/`AuditLogger` classes directly (zero changes to that file). Registered as a project-scoped `PreToolUse` hook in this repo's own `.claude/settings.local.json`. Fail-open on any hook error, with a visible `systemMessage`.

**Tech Stack:** Python 3.13 (stdlib `tomllib`), `watchdog` + `requests` (already installed, confirmed — only needed because `aifs_watcher.py` imports them at module level, unused by the classes this hook actually calls), pytest + `subprocess` for testing (hooks aren't directly unit-testable — the stdin-JSON-in/stdout-JSON-out contract is, via subprocess).

**Spec:** `docs/superpowers/specs/2026-08-16-aifs-claude-hook-design.md`

## Global Constraints

- Zero modifications to `AIFS/aifs_watcher.py` — reuse its classes, don't touch the file.
- Fail-open on any hook exception: return `allow` + a `systemMessage` naming the error, never a silent bypass and never a crash/non-JSON output.
- Project-scoped registration only (this repo's `.claude/settings.local.json`) — not global, not other repos.
- Contracts for `Write`/`Edit` calls whose `file_path` falls outside this repo's root are out of scope for this hook — always `allow`.
- No new dependencies beyond what's already installed and confirmed importable.
- Hooks load at Claude Code session start — a config/script change here does not take effect in the session that made it.

---

### Task 1: Hook script + pilot contract fixtures + automated tests

**Files:**
- Create: `AIFS/aifs_claude_hook.py`
- Create: `AIFS/_hook_test/ext-restricted/manifest.toml`
- Create: `AIFS/_hook_test/ailock-guarded/.ailock`
- Create: `AIFS/_hook_test/trust-tier/TRUST.md`
- Test: `tests/test_aifs_claude_hook.py`

**Interfaces:**
- Produces: `AIFS/aifs_claude_hook.py`, invoked as `python3 aifs_claude_hook.py` with a
  PreToolUse JSON payload (`{"tool_name": ..., "tool_input": {"file_path": ...}}`) on
  stdin, printing `{"hookSpecificOutput": {"permissionDecision": "allow"|"deny"|"ask"}, "systemMessage"?: str}`
  to stdout. Consumed by Task 2's settings.json registration.
- Consumes: `ContractResolver`, `AIFSEnforcer`, `AuditLogger` from the existing
  `AIFS/aifs_watcher.py` (unchanged, read-only dependency).

- [ ] **Step 1: Create the pilot contract fixtures**

`AIFS/_hook_test/ext-restricted/manifest.toml`:

```toml
[contract]
read_only = false
inherit = true

[permissions]
create = [".md"]
edit = [".md"]
delete = false
```

`AIFS/_hook_test/ailock-guarded/.ailock`:

```
# Hard-stop pattern for the AIFS hook pilot test
secret.*
```

`AIFS/_hook_test/trust-tier/TRUST.md`:

```markdown
# TRUST — AIFS Hook Pilot (trust-tier scenario)

- claude-code: EDIT_ONLY
```

- [ ] **Step 2: Write the failing tests**

Create `tests/test_aifs_claude_hook.py`:

```python
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


def test_ext_restricted_folder_blocks_non_md_create():
    target = str(REPO_ROOT / "AIFS" / "_hook_test" / "ext-restricted" / "probe.py")
    resp = _run_hook("Write", target)
    assert resp["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert "create" in resp["systemMessage"].lower()


def test_ext_restricted_folder_allows_md_create():
    target = str(REPO_ROOT / "AIFS" / "_hook_test" / "ext-restricted" / "probe.md")
    resp = _run_hook("Write", target)
    assert resp["hookSpecificOutput"]["permissionDecision"] == "allow"


def test_ailock_pattern_blocks_regardless_of_extension():
    target = str(REPO_ROOT / "AIFS" / "_hook_test" / "ailock-guarded" / "secret.md")
    resp = _run_hook("Write", target)
    assert resp["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert "ailock" in resp["systemMessage"].lower()


def test_trust_tier_edit_only_blocks_create():
    target = str(REPO_ROOT / "AIFS" / "_hook_test" / "trust-tier" / "new_file.md")
    resp = _run_hook("Write", target)
    assert resp["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert "edit_only" in resp["systemMessage"].lower()


def test_trust_tier_edit_only_allows_edit_of_existing_file():
    existing = REPO_ROOT / "AIFS" / "_hook_test" / "trust-tier" / "existing.md"
    existing.parent.mkdir(parents=True, exist_ok=True)
    existing.write_text("pilot fixture\n", encoding="utf-8")
    resp = _run_hook("Edit", str(existing))
    assert resp["hookSpecificOutput"]["permissionDecision"] == "allow"


def test_path_outside_repo_root_allows():
    resp = _run_hook("Write", "C:/Windows/Temp/outside_repo_probe.md")
    assert resp["hookSpecificOutput"]["permissionDecision"] == "allow"


def test_non_write_edit_tool_allows_without_checking_contract():
    target = str(REPO_ROOT / "AIFS" / "_hook_test" / "ext-restricted" / "probe.py")
    resp = _run_hook("Read", target)
    assert resp["hookSpecificOutput"]["permissionDecision"] == "allow"


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
    assert "error" in resp["systemMessage"].lower()


def test_changelog_gets_a_line_for_each_decision():
    changelog = REPO_ROOT / "AIFS" / "_hook_test" / "ext-restricted" / "CHANGELOG.ai.md"
    if changelog.exists():
        changelog.unlink()
    _run_hook("Write", str(REPO_ROOT / "AIFS" / "_hook_test" / "ext-restricted" / "probe.py"))
    assert changelog.exists()
    content = changelog.read_text(encoding="utf-8")
    assert "BLOCK" in content
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd BROski-Obsidian-Brain-for-HyperFocus-z0ne && python -m pytest tests/test_aifs_claude_hook.py -v`
Expected: FAIL — `FileNotFoundError` / non-zero exit from `subprocess.run` (or a JSON decode error on empty stdout), since `AIFS/aifs_claude_hook.py` doesn't exist yet.

- [ ] **Step 4: Write the hook script**

Create `AIFS/aifs_claude_hook.py`:

```python
#!/usr/bin/env python3
"""AIFS enforcement as a Claude Code PreToolUse hook.

Reuses aifs_watcher.py's ContractResolver/AIFSEnforcer/AuditLogger
directly -- this file is the *trigger* (a PreToolUse hook instead of a
watchdog filesystem observer), not a reimplementation of contract logic.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aifs_watcher import ContractResolver, AIFSEnforcer, AuditLogger  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent  # AIFS/ -> repo root


def _decide(tool_name: str, file_path_str: str) -> dict:
    file_path = Path(file_path_str).resolve()

    try:
        file_path.relative_to(REPO_ROOT)
    except ValueError:
        # Outside this repo -- contracts here are per-project, not
        # workspace-wide. Not this hook's concern.
        return {"hookSpecificOutput": {"permissionDecision": "allow"}}

    if tool_name == "Write":
        action = "edit" if file_path.exists() else "create"
    else:  # Edit
        action = "edit"

    resolver = ContractResolver(REPO_ROOT)
    enforcer = AIFSEnforcer()
    contract = resolver.resolve(file_path)
    result, reason = enforcer.check(action, file_path, contract, agent="claude-code")

    AuditLogger().log(action, file_path, result, reason, agent="claude-code")

    if result == "allow":
        return {"hookSpecificOutput": {"permissionDecision": "allow"}}
    if result == "block":
        return {
            "hookSpecificOutput": {"permissionDecision": "deny"},
            "systemMessage": f"AIFS contract blocked this {action}: {reason}",
        }
    # "approval" -- hand it to Claude Code's own live permission prompt
    # rather than AIFS's Discord-timeout path (a human is right here).
    return {
        "hookSpecificOutput": {"permissionDecision": "ask"},
        "systemMessage": f"AIFS contract requires approval for this {action}: {reason}",
    }


def main() -> None:
    try:
        payload = json.load(sys.stdin)
        tool_name = payload.get("tool_name", "")
        file_path = payload.get("tool_input", {}).get("file_path", "")

        if tool_name not in ("Write", "Edit") or not file_path:
            print(json.dumps({"hookSpecificOutput": {"permissionDecision": "allow"}}))
            return

        print(json.dumps(_decide(tool_name, file_path)))
    except Exception as exc:  # noqa: BLE001 -- fail-open by design, see spec
        print(json.dumps({
            "hookSpecificOutput": {"permissionDecision": "allow"},
            "systemMessage": f"AIFS hook error (allowing through): {exc}",
        }))


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd BROski-Obsidian-Brain-for-HyperFocus-z0ne && python -m pytest tests/test_aifs_claude_hook.py -v`
Expected: PASS — all 10 tests green.

- [ ] **Step 6: Commit**

```bash
git add AIFS/aifs_claude_hook.py AIFS/_hook_test/ tests/test_aifs_claude_hook.py
git commit -m "feat: add AIFS PreToolUse enforcement hook for Claude Code + pilot fixtures"
```

---

### Task 2: Register the hook + document it

**Files:**
- Modify: `.claude/settings.local.json`
- Modify: `WHATS_DONE.md`

**Interfaces:**
- Consumes: `AIFS/aifs_claude_hook.py` from Task 1 (invoked by path, no code-level interface).

- [ ] **Step 1: Register the PreToolUse hook**

In `.claude/settings.local.json`, add a new entry to the existing `"PreToolUse": [...]` array
(alongside the existing `Bash`-matcher entry — do not remove or modify that one):

```json
{
  "matcher": "Write|Edit",
  "hooks": [
    {
      "type": "command",
      "command": "python3 \"H:/HYPERFOCUSZONE/HperCore/BROski-Obsidian-Brain-for-HyperFocus-z0ne/AIFS/aifs_claude_hook.py\"",
      "shell": "powershell",
      "timeout": 15,
      "statusMessage": "Checking AIFS folder contract..."
    }
  ]
}
```

- [ ] **Step 2: Validate the JSON**

Run: `cd BROski-Obsidian-Brain-for-HyperFocus-z0ne && python -c "import json; json.load(open('.claude/settings.local.json'))" && echo "valid JSON"`
Expected: `valid JSON` — confirms the edit didn't break the existing file's syntax. This is
config, not code — there is no automated way to verify the hook actually fires without
restarting the Claude Code session (see Step 3).

- [ ] **Step 3: Document the restart requirement + what shipped**

Add to `WHATS_DONE.md` (top of file, new dated entry above the existing 2026-08-16 entry
if one already exists from a prior task this session, otherwise as the newest entry):

```markdown
## 2026-08-16 — AIFS Claude Code enforcement hook (real prevention, not just logging)

`AIFS/aifs_claude_hook.py` (new) makes AIFS folder contracts genuinely
preventive for Claude Code `Write`/`Edit` calls in this repo — a real
`PreToolUse` hook returning `allow`/`deny`/`ask`, not just an
after-the-fact `CHANGELOG.ai.md` entry the way `aifs_watcher.py`'s
filesystem-event watcher works. Reuses `ContractResolver`/`AIFSEnforcer`/
`AuditLogger` from `aifs_watcher.py` directly — zero changes to that
file. Project-scoped (this repo's own `.claude/settings.local.json`
only, not global). Fail-open on any hook error. Pilot contracts at
`AIFS/_hook_test/{ext-restricted,ailock-guarded,trust-tier}/` exercise
each enforcement mechanism independently. 10 tests
(`tests/test_aifs_claude_hook.py`), all via real subprocess invocation
of the hook script (its stdin-JSON-in/stdout-JSON-out contract), not
mocked. Spec: `docs/superpowers/specs/2026-08-16-aifs-claude-hook-design.md`.

⚠️ **Not yet live-verified.** Hooks load at Claude Code session start —
this won't take effect until the next session opens in this repo. First
task next session: attempt a real `Write` to
`AIFS/_hook_test/ext-restricted/probe.py` and confirm the permission
denial actually appears, per the spec's Testing Plan step 7.

**Known limitation (by design, not a gap):** Bash can bypass this
entirely (`echo > file`, `rm`, etc. aren't `Write`/`Edit` tool calls).
This narrows the surface, it doesn't close it completely.
```

- [ ] **Step 4: Commit**

```bash
git add .claude/settings.local.json WHATS_DONE.md
git commit -m "feat: register AIFS PreToolUse hook, document restart requirement"
```

---

## Self-Review Notes

- **Spec coverage:** hook script (Task 1 Step 4), pilot fixtures covering all 3
  enforcement mechanisms independently (Task 1 Step 1), fail-open behavior (tested,
  Task 1 Step 2's malformed-stdin test), `CHANGELOG.ai.md` logging (tested), outside-repo
  path handling (tested), registration (Task 2 Step 1), the "requires restart, not yet
  live-verified" caveat (Task 2 Step 3) — every spec section has a task. Task 3 of the
  spec's Testing Plan is deliberately NOT a task here — it requires a session restart,
  which can't happen mid-implementation; Task 2 Step 3 documents it as the explicit
  first-next-session item instead of pretending it was verified.
- **Placeholder scan:** no TBD/TODO; every code block is complete, runnable code.
- **Type consistency:** `_decide()`'s return shape (`{"hookSpecificOutput": {...}}`,
  optionally `+ "systemMessage"`) matches what every test in Task 1 asserts against
  exactly (`resp["hookSpecificOutput"]["permissionDecision"]`, `resp["systemMessage"]`).
  `AIFSEnforcer.check()`'s call signature and `AuditLogger.log()`'s call signature match
  their actual definitions in `aifs_watcher.py` (verified by reading that file directly
  during the spec's design phase, not assumed).
