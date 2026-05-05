#!/usr/bin/env python3
"""
github_webhook_server.py
Real-time GitHub webhook receiver for THE HYPER BRAIN.
Writes issues, PRs, and actions directly to vault inbox.
Validates HMAC signatures for security.
BROski♾️
"""

import asyncio
import hmac
import hashlib
import json
import os
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse

app = FastAPI(title="Hyper Brain Webhook Receiver")

VAULT_PATH = os.environ.get("OBSIDIAN_VAULT_PATH", "/vault")
WEBHOOK_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET", "")


def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify GitHub webhook HMAC signature."""
    if not secret:
        return True  # Dev mode

    expected = "sha256=" + hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)


@app.post("/webhook/github")
async def github_webhook(
    request: Request,
    x_github_event: str = Header(None),
    x_hub_signature_256: str = Header(None)
):
    """Receive and process GitHub webhooks."""
    payload = await request.body()

    # Validate signature
    if not verify_signature(payload, x_hub_signature_256 or "", WEBHOOK_SECRET):
        raise HTTPException(401, "Invalid signature")

    data = json.loads(payload)
    event = x_github_event or "unknown"

    # Route to handler
    handlers = {
        "issues": _handle_issue,
        "pull_request": _handle_pr,
        "push": _handle_push,
        "release": _handle_release,
    }

    handler = handlers.get(event, _handle_unknown)
    result = await handler(data)

    return {"received": True, "event": event, **result}


async def _handle_issue(data: Dict) -> Dict:
    """Process issue events."""
    repo = data.get("repository", {}).get("name", "unknown")
    action = data.get("action", "unknown")
    issue = data.get("issue", {})

    inbox_path = os.path.join(VAULT_PATH, "00-Inbox", "GitHub")
    os.makedirs(inbox_path, exist_ok=True)

    note = f"""---
created: {datetime.utcnow().isoformat()}
repo: {repo}
event: issues
action: {action}
number: {issue.get('number', 0)}
title: {issue.get('title', '')}
status: {issue.get('state', 'open')}
labels: {json.dumps([l['name'] for l in issue.get('labels', [])])}
assignee: {issue.get('assignee', {}).get('login', 'unassigned')}
tags: [github, issue, {repo}, {action}]
---
# 🐛 {repo} #{issue.get('number', 0)} — {issue.get('title', '')}

**Action**: {action}
**State**: {issue.get('state', 'unknown')}
**Author**: @{issue.get('user', {}).get('login', 'unknown')}
**URL**: {issue.get('html_url', '')}

## Body
{issue.get('body', '')[:1000]}

---
*Received via webhook at {datetime.utcnow().strftime('%H:%M:%S')}*
"""

    fname = f"{repo}_issue_{issue.get('number', 0)}_{action}.md"
    with open(os.path.join(inbox_path, fname), "w", encoding="utf-8") as f:
        f.write(note)

    return {"file": fname, "repo": repo, "number": issue.get('number', 0)}


async def _handle_pr(data: Dict) -> Dict:
    """Process pull request events."""
    repo = data.get("repository", {}).get("name", "unknown")
    action = data.get("action", "unknown")
    pr = data.get("pull_request", {})

    inbox_path = os.path.join(VAULT_PATH, "00-Inbox", "GitHub")
    os.makedirs(inbox_path, exist_ok=True)

    note = f"""---
created: {datetime.utcnow().isoformat()}
repo: {repo}
event: pull_request
action: {action}
number: {pr.get('number', 0)}
title: {pr.get('title', '')}
status: {pr.get('state', 'open')}
branch: {pr.get('head', {}).get('ref', 'unknown')} → {pr.get('base', {}).get('ref', 'unknown')}
tags: [github, pr, {repo}, {action}]
---
# 🔀 {repo} #{pr.get('number', 0)} — {pr.get('title', '')}

**Action**: {action}
**State**: {pr.get('state', 'unknown')}
**Author**: @{pr.get('user', {}).get('login', 'unknown')}
**URL**: {pr.get('html_url', '')}

## Description
{pr.get('body', '')[:1000]}

---
*Received via webhook at {datetime.utcnow().strftime('%H:%M:%S')}*
"""

    fname = f"{repo}_pr_{pr.get('number', 0)}_{action}.md"
    with open(os.path.join(inbox_path, fname), "w", encoding="utf-8") as f:
        f.write(note)

    return {"file": fname, "repo": repo, "number": pr.get('number', 0)}


async def _handle_push(data: Dict) -> Dict:
    """Process push events."""
    repo = data.get("repository", {}).get("name", "unknown")
    commits = data.get("commits", [])

    # Award BROski$ for commits (future: integrate with economy API)
    return {
        "repo": repo,
        "commits": len(commits),
        "message": f"{len(commits)} commits pushed to {repo}"
    }


async def _handle_release(data: Dict) -> Dict:
    """Process release events."""
    repo = data.get("repository", {}).get("name", "unknown")
    release = data.get("release", {})

    return {
        "repo": repo,
        "tag": release.get("tag_name", "unknown"),
        "message": f"🚀 {repo} {release.get('tag_name')} released!"
    }


async def _handle_unknown(data: Dict) -> Dict:
    return {"message": "Event type not handled, but logged"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8101)
