#!/usr/bin/env python3
"""AIFS enforcement as a Claude Code PreToolUse hook.

Reuses aifs_watcher.py's ContractResolver/AIFSEnforcer/AuditLogger
directly -- this file is the *trigger* (a PreToolUse hook instead of a
watchdog filesystem observer), not a reimplementation of contract logic.
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent  # AIFS/ -> repo root


def _decide(tool_name: str, file_path_str: str) -> dict:
    # Strip an extended-length Windows path prefix (\\?\ or //?/) before
    # resolving. Without this, a caller could smuggle a path outside the
    # repo boundary check: Path.resolve() preserves the prefix, and the
    # resulting string comparison in relative_to() would never match
    # REPO_ROOT even for a path that is genuinely inside the repo (or,
    # depending on normalization, dodge the check the other way).
    for prefix in ("\\\\?\\", "//?/"):
        if file_path_str.startswith(prefix):
            file_path_str = file_path_str[len(prefix):]
            break

    file_path = Path(file_path_str).resolve()

    try:
        file_path.relative_to(REPO_ROOT)
    except ValueError:
        # Outside this repo -- contracts here are per-project, not
        # workspace-wide. Not this hook's concern.
        return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}}

    # Imported here (not at module level, and only after the repo-boundary
    # check above) so that an import failure -- missing watchdog/requests/
    # tomllib on whatever interpreter ends up running this script, or any
    # future change to aifs_watcher.py's own imports -- is caught by
    # main()'s try/except and fails open, instead of crashing before any
    # exception handler exists. Deferring past the repo-boundary check also
    # means out-of-repo Write/Edit calls (which never need contract
    # resolution) don't pay this import's cost.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from aifs_watcher import ContractResolver, AIFSEnforcer, AuditLogger  # noqa: E402

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
        return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}}
    if result == "block":
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"AIFS contract blocked this {action}: {reason}",
            },
            "systemMessage": f"AIFS contract blocked this {action}: {reason}",
        }
    # "approval" -- hand it to Claude Code's own live permission prompt
    # rather than AIFS's Discord-timeout path (a human is right here).
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": f"AIFS contract requires approval for this {action}: {reason}",
        },
        "systemMessage": f"AIFS contract requires approval for this {action}: {reason}",
    }


def main() -> None:
    try:
        payload = json.load(sys.stdin)
        tool_name = payload.get("tool_name", "")
        file_path = payload.get("tool_input", {}).get("file_path", "")

        if tool_name not in ("Write", "Edit") or not file_path:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}}))
            return

        print(json.dumps(_decide(tool_name, file_path)))
    except Exception as exc:  # noqa: BLE001 -- fail-open by design, see spec
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
                "permissionDecisionReason": f"AIFS hook error (allowing through): {exc}",
            },
            "systemMessage": f"AIFS hook error (allowing through): {exc}",
        }))


if __name__ == "__main__":
    main()
