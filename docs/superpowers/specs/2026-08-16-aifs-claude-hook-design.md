# AIFS Claude Code Enforcement Hook — Design

## Context & Constraints

- AIFS ("AI File System — The Folder Contract Protocol for AI Agents") is
  a complete, separately-versioned product living in `AIFS/` — full
  roadmap v0.1→v1.0 shipped, including a real-time watcher
  (`aifs_watcher.py`), MCP server, signing, a dashboard, and a public
  registry. Not a half-built internal utility — treat it as
  finished/stable code, not something to be redesigned.
- `AIFS/aifs_watcher.py`'s `ContractResolver` + `AIFSEnforcer` classes
  already implement the full contract-resolution and allow/block/approval
  decision logic (folder-contract lookup via `manifest.toml`/`.ailock`/
  `TRUST.md`/`ttl.toml`/`context.md`, walked up the tree, merged with
  parent contracts). This spec reuses those classes directly — it does
  not reimplement contract semantics.
- **`aifs_watcher.py`'s actual enforcement is detective, not preventive.**
  It's built on `watchdog` filesystem events (`on_created`/`on_modified`/
  etc.), which fire *after* a write has already landed on disk. A
  `"block"` verdict there means "log that this shouldn't have happened,"
  not "stop it from happening." This was confirmed by reading the file in
  full, not assumed from its docstring.
- Claude Code's own `PreToolUse` hook mechanism is a genuine
  interception point — it runs *before* a `Write`/`Edit` tool call
  executes and can return `permissionDecision: "deny"` to actually stop
  it. This is the only real prevention mechanism available; nothing in
  AIFS itself provides one.
- This repo's own `.claude/settings.local.json` already has working
  `PreToolUse`/`PostToolUse`/`SessionStart`/`SessionEnd` hooks (Discord
  XP rewards, compose validation, env guard) — this spec follows that
  file's existing conventions (PowerShell shell, `python3` invocation,
  `Write|Edit` matcher already in use for `PostToolUse`) rather than
  inventing a new hook style.
- Verified in this environment: Python 3.13.5, with `tomllib`,
  `watchdog`, and `requests` all already importable — `aifs_watcher.py`
  can be imported from directly with zero modification and zero new
  dependencies.
- Hooks load at Claude Code session start — a hook config or script
  change does not take effect in the session that made the change, only
  the next one.

## Goal

A `PreToolUse` hook that, for `Write`/`Edit` tool calls in this repo,
resolves the AIFS folder contract for the target file (reusing
`aifs_watcher.py`'s own logic) and returns a real `allow`/`deny`/`ask`
decision to Claude Code — genuine prevention, not just logging. Folders
with no contract behave exactly as `AIFSEnforcer`'s existing safe
defaults already specify (unrestricted create/edit, delete blocked) —
this hook changes *when* that logic runs, not what it decides.

## Design

### 1. `AIFS/aifs_claude_hook.py` (new file, co-located with `aifs_watcher.py`)

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

Fail-open is deliberate (per the confirmed decision above): any
exception — missing import, bad JSON, a contract-parsing bug — is caught
and returns `allow` with a visible `systemMessage`, never a silent
bypass and never a silent full-repo lockout. Matches HyperFlow/Safety
Shepherd's fail-open-on-unreachable precedent, not coder-studio's
fail-closed (that gates a fully-autonomous loop; this gates a session
Bro is watching live).

### 2. Registration — `.claude/settings.local.json` (this repo, project-scoped)

Add a new `PreToolUse` entry (the existing file already has one for
`Bash`, and a `PostToolUse` one for `Write|Edit` — this is a new,
separate `PreToolUse` entry for `Write|Edit`, same style):

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

Project-scoped (this repo only), not global — see spec Context: a
misbehaving hook here has a contained blast radius, not a workspace-wide
one. Expanding to other repos is a separate, later decision.

### 3. Pilot contract — `AIFS/_hook_test/`

A new throwaway folder, not a real working folder, so the first test has
zero risk to real repo content:

- `AIFS/_hook_test/manifest.toml` — restrict `create`/`edit` to `.md`
  only, matching the `[permissions]` shape `aifs_watcher.py` already
  parses.
- `AIFS/_hook_test/.ailock` — one hard-stop pattern (e.g. `secret.*`) to
  verify the block path independent of the manifest.
- `AIFS/_hook_test/TRUST.md` — `- claude-code: EDIT_ONLY` to verify the
  trust-tier path (blocks `create`/`delete`, allows `edit`).

## API/Behaviour Summary

| Scenario | Result |
|---|---|
| `Edit`/`Write` inside `AIFS/_hook_test/`, `.md` file, no `.ailock` match | `allow` |
| `Write` (create) a new `.py` file in `AIFS/_hook_test/` (manifest restricts to `.md`) | `deny`, reason surfaced in `systemMessage` |
| `Edit`/`Write` a file matching the `.ailock` pattern | `deny`, hard stop |
| `Write` (create) in `AIFS/_hook_test/` — `TRUST.md` says `claude-code: EDIT_ONLY` | `deny` (EDIT_ONLY blocks create) |
| `Edit` an existing file in `AIFS/_hook_test/` under the same `EDIT_ONLY` tier | `allow` |
| Any `Write`/`Edit` outside this repo's root | `allow` (out of scope for this hook) |
| Any `Write`/`Edit` in a folder with no contract anywhere up the tree | `allow` for create/edit, per `AIFSEnforcer`'s existing safe defaults — unchanged by this spec |
| Hook script raises an exception | `allow`, with a visible `systemMessage` naming the error |

## Error Handling

Every decision path also writes to the resolved folder's
`CHANGELOG.ai.md` via the existing `AuditLogger`, so even an `allow`
decision leaves a record — matches what the real watcher would have
logged, just triggered differently.

## Testing Plan

No existing test suite for `AIFS/` (it's a standalone product, not
wired into this repo's test tooling) — this hook gets its own minimal
one:

**Manual verification** (hooks can't be unit-tested via pytest the same
way — they're driven by the Claude Code harness, not importable as a
function with a clean call signature independent of stdin/stdout):
1. Pipe a synthetic `Write`-on-new-`.py`-file JSON payload to
   `aifs_claude_hook.py` directly via stdin, confirm `deny` + correct
   reason, against the pilot contract.
2. Same for a `.md` file in the same folder — confirm `allow`.
3. Same for a file matching the `.ailock` pattern — confirm `deny`,
   hard-stop reason.
4. Confirm `CHANGELOG.ai.md` gets a line for each of the above.
5. Confirm a file path outside `REPO_ROOT` returns `allow` without
   touching the contract logic at all.
6. Confirm a forced exception (e.g. temporarily break the import path)
   still returns `allow` with a `systemMessage`, never a crash/non-JSON
   output.
7. **Live check, next session** (hooks require a restart to load): open
   a fresh Claude Code session in this repo, attempt a real `Write` to a
   restricted path in `AIFS/_hook_test/`, confirm the permission prompt/
   denial actually appears.

## Out of Scope (named, not silently ignored)

- **Bash can bypass this entirely.** `echo > file` or any shell
  redirect/`cp`/`mv` isn't a `Write`/`Edit` tool call, so this hook never
  sees it. A determined bypass exists; this hook narrows the surface, it
  doesn't close it completely.
- **Other agents/tools in this workspace are unaffected.** This is a
  Claude-Code-specific `PreToolUse` hook — it says nothing about what any
  other AI tool, script, or human editing this repo can do.
- **Global (all-repos) enforcement** — deliberately deferred; see
  Context. A future, separate decision once this pilot is proven.
- **Real Discord-approval polling for the `"ask"` verdict** — this spec
  routes `approval` results to Claude Code's own permission UI instead,
  which didn't exist when AIFS's `DiscordApprovalGate` was built. AIFS's
  own Discord path is untouched, just not used by this hook.
