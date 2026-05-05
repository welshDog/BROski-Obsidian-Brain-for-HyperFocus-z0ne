"""HYPER BRAIN v3.0 — GitHub Webhook Server
Level 14 | Real-time GitHub issues + PRs → instant vault writes
"""
import os
import json
import hmac
import hashlib
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException, Header
from typing import Optional

VAULT_PATH = Path(os.environ.get("VAULT_PATH", "/vault"))
GITHUB_WEBHOOK_SECRET = os.environ.get("GITHUB_WEBHOOK_SECRET", "")
GITHUB_DIR = VAULT_PATH / "HYPERFOCUS_ZONE" / "GitHub"

app = FastAPI(title="HYPER BRAIN GitHub Webhook Server", version="3.0.0")


def verify_signature(payload: bytes, signature: str) -> bool:
    if not GITHUB_WEBHOOK_SECRET:
        return True  # Skip verification if no secret set
    expected = "sha256=" + hmac.new(
        GITHUB_WEBHOOK_SECRET.encode(), payload, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


def write_to_vault(event_type: str, data: dict, filename: str):
    """Write a GitHub event to the Obsidian vault."""
    GITHUB_DIR.mkdir(parents=True, exist_ok=True)

    # Write JSON for machine reading
    json_file = GITHUB_DIR / "recent_activity.json"
    existing = []
    if json_file.exists():
        try:
            existing = json.loads(json_file.read_text()).get("items", [])
        except Exception:
            existing = []
    existing.insert(0, {"type": event_type, **data})
    existing = existing[:50]  # Keep last 50 events
    json_file.write_text(json.dumps({"items": existing, "updated": datetime.now().isoformat()}, indent=2))

    # Write human-readable MD
    md_file = GITHUB_DIR / filename
    md_file.write_text(data.get("markdown", json.dumps(data, indent=2)))
    print(f"✅ Vault updated: {filename}")


@app.post("/webhook/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: Optional[str] = Header(None),
    x_github_event: Optional[str] = Header(None)
):
    payload = await request.body()

    if x_hub_signature_256 and not verify_signature(payload, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")

    try:
        data = json.loads(payload)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    event = x_github_event or "unknown"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if event == "issues":
        action = data.get("action", "unknown")
        issue = data.get("issue", {})
        repo = data.get("repository", {}).get("full_name", "unknown")
        md = f"""# 🐙 GitHub Issue {action.capitalize()}

**Repo:** {repo}
**Issue #{issue.get('number')}:** {issue.get('title', 'Unknown')}
**State:** {issue.get('state', 'unknown')}
**Author:** {issue.get('user', {}).get('login', 'unknown')}
**Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Body
{issue.get('body', 'No description') or 'No description'}

**Labels:** {', '.join(l['name'] for l in issue.get('labels', []))}
**URL:** {issue.get('html_url', '')}
"""
        write_to_vault("issue", {
            "title": issue.get("title"),
            "number": issue.get("number"),
            "action": action,
            "repo": repo,
            "markdown": md
        }, f"issue_{issue.get('number', timestamp)}.md")

    elif event == "pull_request":
        action = data.get("action", "unknown")
        pr = data.get("pull_request", {})
        repo = data.get("repository", {}).get("full_name", "unknown")
        md = f"""# 🔀 Pull Request {action.capitalize()}

**Repo:** {repo}
**PR #{pr.get('number')}:** {pr.get('title', 'Unknown')}
**State:** {pr.get('state', 'unknown')}
**Author:** {pr.get('user', {}).get('login', 'unknown')}
**Branch:** {pr.get('head', {}).get('ref', 'unknown')} → {pr.get('base', {}).get('ref', 'unknown')}
**Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Description
{pr.get('body', 'No description') or 'No description'}

**URL:** {pr.get('html_url', '')}
"""
        write_to_vault("pull_request", {
            "title": pr.get("title"),
            "number": pr.get("number"),
            "action": action,
            "repo": repo,
            "markdown": md
        }, f"pr_{pr.get('number', timestamp)}.md")

    elif event == "push":
        repo = data.get("repository", {}).get("full_name", "unknown")
        commits = data.get("commits", [])
        ref = data.get("ref", "").replace("refs/heads/", "")
        md = f"""# 🚀 Push to {repo}/{ref}

**Branch:** {ref}
**Commits:** {len(commits)}
**Pusher:** {data.get('pusher', {}).get('name', 'unknown')}
**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Commits
""" + "\n".join(f"- `{c.get('id', '')[:7]}` {c.get('message', '')}" for c in commits[:10])
        write_to_vault("push", {
            "title": f"Push to {repo}/{ref}",
            "commits": len(commits),
            "markdown": md
        }, f"push_{timestamp}.md")

    return {"status": "ok", "event": event, "processed": True}


@app.get("/health")
async def health():
    return {"status": "online", "service": "github-webhook-server", "version": "3.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8101)
