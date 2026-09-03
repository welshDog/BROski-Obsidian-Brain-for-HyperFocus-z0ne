#!/usr/bin/env python3
"""HyperFocus Z0ne -- uniform git post-commit XP publisher.

Repo-agnostic: run from inside ANY repo (the post-commit hook's cwd is the
repo). Reads HEAD, awards prefix-based XP, and publishes an `xp_award` to the
Redis `broski_economy` channel so the always-on consumer banks it (redis tally
+ durable postgres wallet via /api/v1/economy/award-dev-xp).

Redis lives on an internal docker network (6379 unpublished -- Sacred Rule:
data-net internal), so we reach it via `docker exec`. Everything here is
best-effort: redis offline / not a repo / no docker == silent exit 0, never
blocks a commit.

Installed into each repo's .git/hooks/post-commit by
scripts/install_xp_hooks.sh (sibling). HyperCode-V2.4 is intentionally NOT
wired here -- it has its own richer hook (scripts/pets/git_post_commit.py).
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone

_CHANNEL = "broski_economy"
_DB = 1  # Sacred Rule: DB 1 = cache
_REDIS_CONTAINERS = ("redis", "hypercode-redis")

# Conventional-commit prefix -> XP (mirrors HyperCode-V2.4 git_post_commit.py).
_PREFIX_XP = {"fix": 25, "test": 20, "feat": 15, "refactor": 10, "docs": 5, "chore": 5}
_DEFAULT_XP = 10


def _git(args):
    return subprocess.check_output(
        ["git", *args], stderr=subprocess.DEVNULL
    ).decode("utf-8", errors="replace").strip()


def _patch_id():
    """Stable-across-rebase commit identity: same diff -> same id, so a rebase
    replay dedups against the original award. Falls back to HEAD sha."""
    try:
        # text=True defaults to the locale codec (cp1252 on Windows) for the
        # pipe reader thread -> a diff with any non-cp1252 byte (emoji, arrows,
        # accented note titles) crashes the hook. Pin utf-8 + replace.
        diff = subprocess.run(["git", "diff-tree", "-p", "--root", "HEAD"],
                              capture_output=True, text=True, timeout=8,
                              encoding="utf-8", errors="replace")
        pid = subprocess.run(["git", "patch-id", "--stable"],
                             input=diff.stdout, capture_output=True, text=True, timeout=8,
                             encoding="utf-8", errors="replace")
        tok = pid.stdout.strip().split()
        if tok:
            return tok[0]
    except Exception:
        pass
    try:
        return _git(["rev-parse", "HEAD"])
    except Exception:
        return "unknown"


def _publish(payload):
    body = json.dumps(payload)
    try:
        import shutil
        if not shutil.which("docker"):
            return None
        for container in _REDIS_CONTAINERS:
            proc = subprocess.run(
                ["docker", "exec", container, "redis-cli", "-n", str(_DB),
                 "PUBLISH", _CHANNEL, body],
                capture_output=True, text=True, timeout=8,
                encoding="utf-8", errors="replace",
            )
            if proc.returncode == 0:
                return "docker:" + container
    except Exception:
        pass
    return None


def main():
    try:
        repo_root = _git(["rev-parse", "--show-toplevel"])
        subject = _git(["log", "-1", "--pretty=%s"])
    except Exception:
        return 0  # not a repo / no commits -- nothing to do

    repo_name = os.path.basename(repo_root) if repo_root else "unknown"
    prefix = subject.split(":", 1)[0].strip().lower() if ":" in subject else ""
    xp = _PREFIX_XP.get(prefix, _DEFAULT_XP)
    reason = f"git commit: {subject}" if subject else "git commit"

    published = _publish({
        "event": "xp_award",
        "xp": xp,
        "reason": reason,
        "source": f"git:{repo_name}",
        "source_id": f"git:{repo_name}:{_patch_id()}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    if published:
        sys.stderr.write(f"[broski_economy] +{xp} XP  git:{repo_name}  ({reason})  -> {published}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
