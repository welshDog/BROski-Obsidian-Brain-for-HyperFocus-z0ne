#!/usr/bin/env python3
"""
hyper_brain_ops.py
Maintains the Hyper Brain infrastructure. Verifies container health, triggers the
morning briefing, syncs cross-repo GitHub issues, and delivers a Discord report.
"""

import argparse
import json
import os
import sys
import time
import subprocess
from urllib import error as urllib_error
from urllib import parse as urllib_parse
from urllib import request as urllib_request
from datetime import datetime

# Force UTF-8 for Windows PowerShell emoji support
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Load .env file manually to avoid third-party dependencies
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"\''))

class RateLimitError(Exception):
    """Raised when the API rate limit is exceeded."""

class APIClient:
    """Base client with built-in rate limiting."""
    def __init__(self, requests_per_second=1):
        self.delay = 1.0 / requests_per_second
        self.last_request_time = 0.0

    def _wait_for_rate_limit(self):
        elapsed = time.monotonic() - self.last_request_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)

    def _request(self, url, method="GET", headers=None, data=None, retries=3):
        headers = headers or {}
        for attempt in range(retries):
            self._wait_for_rate_limit()
            try:
                req = urllib_request.Request(url, method=method, headers=headers, data=data)
                with urllib_request.urlopen(req, timeout=30) as response:
                    self.last_request_time = time.monotonic()
                    resp_body = response.read()
                    if resp_body:
                        try:
                            return json.loads(resp_body.decode('utf-8'))
                        except json.JSONDecodeError:
                            return resp_body.decode('utf-8')
                    return None
            except urllib_error.HTTPError as e:
                self.last_request_time = time.monotonic()
                if e.code == 429:
                    wait = 2**attempt
                    print(f'Rate limited (429), retrying in {wait}s...', file=sys.stderr)
                    if attempt == retries - 1:
                        raise RateLimitError(f'HTTP 429 Too Many Requests from {url}.') from e
                    time.sleep(wait)
                    continue
                if e.code >= 500:
                    wait = 2**attempt
                    print(f'Server error {e.code}, retrying in {wait}s...', file=sys.stderr)
                    if attempt == retries - 1:
                        raise RuntimeError(f'Server error {e.code} from {url}.') from e
                    time.sleep(wait)
                    continue
                
                try:
                    body = e.read().decode('utf-8', errors='replace')[:1000]
                except OSError:
                    body = e.reason
                raise RuntimeError(f'HTTP {e.code} from {url}: {body}') from e
            except urllib_error.URLError as e:
                if attempt == retries - 1:
                    raise RuntimeError(f'Failed to connect to {url}: {e}') from e
                time.sleep(2**attempt)

def write_output(data, output_file):
    if not output_file:
        return
    os.makedirs(os.path.dirname(os.path.abspath(output_file)) or ".", exist_ok=True)
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f'✅ Output written to: {output_file}')
    except Exception as e:
        print(f'❌ Error writing output to {output_file}: {e}', file=sys.stderr)

def fix_env(args):
    """Check required environment variables and paths."""
    print("🔍 Checking Environment...")
    issues = []
    
    pat = os.environ.get("GITHUB_PAT")
    if not pat:
        issues.append("❌ GITHUB_PAT is missing.")
    else:
        print("✅ GITHUB_PAT is set.")
        
    discord = os.environ.get("DISCORD_WEBHOOK_URL")
    if not discord:
        issues.append("❌ DISCORD_WEBHOOK_URL is missing.")
    else:
        print("✅ DISCORD_WEBHOOK_URL is set.")
        
    vault = os.environ.get("VAULT_PATH")
    if not vault:
        issues.append("❌ VAULT_PATH is missing.")
    else:
        if not os.path.exists(vault):
            issues.append(f"❌ VAULT_PATH does not exist: {vault}")
        else:
            print(f"✅ VAULT_PATH exists: {vault}")
            
    if issues:
        print("\n".join(issues))
        sys.exit(1)
    
    print("🚀 Environment is ready!")

def check_health(args):
    client = APIClient()
    status = {"service": "hyper-brain", "status": "unknown"}
    try:
        resp = client._request("http://localhost:8100/health", retries=1)
        status["status"] = "healthy"
        status["details"] = resp
        print("✅ hyper-brain is healthy!")
    except Exception as e:
        status["status"] = "unhealthy"
        status["error"] = str(e)
        print(f"❌ hyper-brain health check failed: {e}")
        
        if getattr(args, 'restart_if_down', False):
            print("🔄 Attempting to restart container...")
            try:
                subprocess.run(["docker", "restart", "hyper-brain"], check=True)
                print("✅ Container restarted.")
                status["restarted"] = True
            except Exception as restart_err:
                print(f"❌ Failed to restart container: {restart_err}")
                status["restart_error"] = str(restart_err)
    
    write_output(status, args.output)

def generate_briefing(args):
    client = APIClient()
    try:
        print("🌅 Triggering morning briefing generation...")
        resp = client._request("http://localhost:8100/briefing/generate", method="POST")
        print("✅ Briefing generated successfully.")
        write_output({"status": "success", "response": resp}, args.output)
    except Exception as e:
        print(f"❌ Failed to generate briefing: {e}")
        write_output({"status": "error", "error": str(e)}, args.output)

def sync_github(args):
    token = os.environ.get("GITHUB_PAT")
    if not token:
        print("❌ GITHUB_PAT not set. Cannot sync.")
        sys.exit(1)
        
    vault_path = os.environ.get("VAULT_PATH")
    if not vault_path:
        print("❌ VAULT_PATH not set. Cannot sync.")
        sys.exit(1)
        
    inbox_dir = os.path.join(vault_path, "00-Inbox", "GitHub")
    os.makedirs(inbox_dir, exist_ok=True)
    
    repos = [
        "welshDog/HyperCode-V2.4",
        "welshDog/HyperAgent-SDK",
        "welshDog/BROskiPets-LLM-dNFT",
        "welshDog/Hyper-Vibe-Coding-Course"
    ]
    
    client = APIClient(requests_per_second=2) # 2 req/s limit for GitHub API
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    
    results = {"synced_repos": [], "errors": []}
    
    for repo in repos:
        url = f"https://api.github.com/repos/{repo}/issues?state=open&per_page=50"
        try:
            issues = client._request(url, headers=headers)
            issues = [i for i in issues if "pull_request" not in i]
            repo_name = repo.split("/")[1]
            
            lines = [
                f"# 🐛 {repo_name} — Open Issues\n",
                f"*Synced: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n",
                f"*Total: {len(issues)} open issues*\n",
                "---\n"
            ]
            
            if not issues:
                lines.append("✅ No open issues. BROski clean!\n")
            else:
                for issue in issues:
                    assignee = issue["assignee"]["login"] if issue.get("assignee") else "unassigned"
                    labels = ", ".join([l["name"] for l in issue.get("labels", [])]) or "none"
                    lines.append(f"- [ ] #{issue['number']} — {issue['title']}")
                    lines.append(f"  - 🔗 {issue['html_url']}")
                    lines.append(f"  - 👤 {assignee} | 🏷️ {labels}")
                    lines.append("")
                    
            out_file = os.path.join(inbox_dir, f"{repo_name}.md")
            with open(out_file, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
                
            print(f"✅ Synced: {repo_name} ({len(issues)} issues)")
            results["synced_repos"].append({"repo": repo_name, "issues": len(issues)})
        except Exception as e:
            print(f"⚠️ Failed to sync {repo}: {e}")
            results["errors"].append({"repo": repo, "error": str(e)})
            
    write_output(results, args.output)

def send_report(args):
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("❌ DISCORD_WEBHOOK_URL not set.")
        sys.exit(1)
        
    # Gather reports if available
    health_status = "Unknown"
    briefing_status = "Unknown"
    sync_status = "Unknown"
    
    # Check outputs dir
    output_dir = "output"
    if os.path.exists(os.path.join(output_dir, "health.json")):
        try:
            with open(os.path.join(output_dir, "health.json")) as f:
                d = json.load(f)
                health_status = "✅ Healthy" if d.get("status") == "healthy" else f"❌ {d.get('error', 'Unhealthy')}"
                if d.get("restarted"): health_status += " (Restarted)"
        except: pass
        
    if os.path.exists(os.path.join(output_dir, "briefing.json")):
        try:
            with open(os.path.join(output_dir, "briefing.json")) as f:
                d = json.load(f)
                briefing_status = "✅ Generated" if d.get("status") == "success" else f"❌ Failed: {d.get('error', '')}"
        except: pass
        
    if os.path.exists(os.path.join(output_dir, "sync.json")):
        try:
            with open(os.path.join(output_dir, "sync.json")) as f:
                d = json.load(f)
                count = sum(r.get("issues", 0) for r in d.get("synced_repos", []))
                errs = len(d.get("errors", []))
                sync_status = f"✅ Synced ({count} issues)" if errs == 0 else f"⚠️ {errs} errors syncing"
        except: pass
        
    payload = {
        "content": None,
        "embeds": [
            {
                "title": "🧠 Hyper Brain Daily Ops Report",
                "description": "Morning operations completed.",
                "color": 5814783,
                "fields": [
                    {"name": "🐳 Engine Health", "value": health_status, "inline": False},
                    {"name": "🌅 Briefing", "value": briefing_status, "inline": False},
                    {"name": "🐙 GitHub Sync", "value": sync_status, "inline": False}
                ],
                "footer": {"text": f"BROski♾️ — {datetime.now().strftime('%Y-%m-%d %H:%M')}"}
            }
        ]
    }
    
    client = APIClient(requests_per_second=1)
    req_data = json.dumps(payload).encode('utf-8')
    headers = {"Content-Type": "application/json", "User-Agent": "HyperBrainOps/1.0"}
    
    try:
        client._request(webhook_url, method="POST", headers=headers, data=req_data)
        print("🔔 Discord report sent successfully.")
    except Exception as e:
        print(f"❌ Failed to send Discord report: {e}")

def main():
    parser = argparse.ArgumentParser(description="Hyper Brain Ops Maintainer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_env = subparsers.add_parser("fix-env", help="Check environment variables")
    
    p_health = subparsers.add_parser("check-health", help="Check container health")
    p_health.add_argument("--output", help="Output JSON path")
    p_health.add_argument("--restart-if-down", action="store_true", help="Restart container if down")
    
    p_briefing = subparsers.add_parser("generate-briefing", help="Trigger morning briefing")
    p_briefing.add_argument("--output", help="Output JSON path")
    
    p_sync = subparsers.add_parser("sync-github", help="Sync GitHub issues")
    p_sync.add_argument("--output", help="Output JSON path")
    
    p_report = subparsers.add_parser("report", help="Send status to Discord")

    args = parser.parse_args()

    if args.command == "fix-env":
        fix_env(args)
    elif args.command == "check-health":
        check_health(args)
    elif args.command == "generate-briefing":
        generate_briefing(args)
    elif args.command == "sync-github":
        sync_github(args)
    elif args.command == "report":
        send_report(args)

if __name__ == "__main__":
    main()
