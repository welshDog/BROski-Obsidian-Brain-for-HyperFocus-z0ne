#!/usr/bin/env python3
"""
hyper_brain_ops.py  v2.0.0
BROski Brain Ops — upgraded with OpsLogger, OperationHandler, circuit breaker,
taxonomy error codes, canonical ops-status.json output, and Obsidian dashboard gen.

Subcommands:
  fix-env             Check required env vars + paths
  check-health        Verify Docker + hyper-brain container + API
  generate-briefing   Trigger morning briefing via API
  sync-github         Sync open issues from all repos into vault
  report              Send status embed to Discord
  run-all             Run full ops chain + write canonical status output

Error code taxonomy: see ops/ops_taxonomy.json in HyperCode-V2.4
"""

import argparse
import json
import os
import sys
import time
import subprocess
from urllib import error as urllib_error
from urllib import request as urllib_request
from datetime import datetime
from typing import Any, Callable, Dict, Optional, Tuple

# ── UTF-8 for Windows PowerShell emoji support ───────────────────────────────
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# ── Load .env (no third-party deps) ──────────────────────────────────────────
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
if os.path.exists(_env_path):
    with open(_env_path, "r", encoding="utf-8") as _f:
        for _line in _f:
            _line = _line.strip()
            if "=" in _line and not _line.startswith("#"):
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip().strip("\"'"))

# ── Constants ─────────────────────────────────────────────────────────────────
OPS_VERSION = "2.0.0"
REPOS = [
    "welshDog/HyperCode-V2.4",
    "welshDog/HyperAgent-SDK",
    "welshDog/BROskiPets-LLM-dNFT",
    "welshDog/Hyper-Vibe-Coding-Course",
]

# Maps exception patterns → taxonomy error codes
ERROR_CODE_MAP = {
    "docker daemon":          "HC_001",
    "hyper-brain":            "HC_002",
    "port 8100":              "HC_004",
    "token invalid":          "GH_001",
    "401":                    "GH_001",
    "rate limit":             "GH_002",
    "429":                    "GH_002",
    "no access":              "GH_003",
    "403":                    "GH_003",
    "not found":              "GH_003",
    "404":                    "GH_003",
    "timeout":                "GH_004",
    "urlopen error":          "GH_004",
    "vault path":             "BR_001",
    "permissionerror":        "BR_001",
    "500":                    "BR_002",
    "template missing":       "BR_003",
    "briefings":              "BR_004",
    "git not initialized":    "VC_001",
    "git config":             "VC_002",
    "merge conflict":         "VC_003",
    "push failed":            "VC_004",
    "webhook":                "DC_001",
    "webhook 401":            "DC_002",
    "webhook 403":            "DC_002",
}

NON_RETRYABLE = {
    "GH_001", "GH_003", "DC_001", "DC_002",
    "VC_001", "VC_002", "BR_001", "BR_003",
}

CIRCUIT_BREAKER_THRESHOLDS = {
    "health_check":        {"failures": 3, "recovery_seconds": 120},
    "github_sync":         {"failures": 5, "recovery_seconds": 300},
    "briefing_generation": {"failures": 3, "recovery_seconds": 300},
    "vault_commit":        {"failures": 3, "recovery_seconds": 120},
    "discord_report":      {"failures": 3, "recovery_seconds": 600},
}


# ═════════════════════════════════════════════════════════════════════════════
# OpsLogger — structured log writer
# ═════════════════════════════════════════════════════════════════════════════
class OpsLogger:
    """
    Writes structured log lines to stdout AND ops.log.
    Format: [TIMESTAMP] [LEVEL] [STEP] [CODE] [MESSAGE]
    """

    LEVELS = {"DEBUG": 0, "INFO": 1, "WARN": 2, "ERROR": 3}

    def __init__(self, log_path: Optional[str] = None, min_level: str = "INFO"):
        self.log_path = log_path
        self.min_level = min_level
        self._entries: list = []

    def _write(self, level: str, step: str, code: str, message: str):
        if self.LEVELS.get(level, 0) < self.LEVELS.get(self.min_level, 0):
            return
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] [{level:<5}] [{step:<22}] [{code}] {message}"
        print(line)
        self._entries.append(line)
        if self.log_path:
            try:
                os.makedirs(os.path.dirname(os.path.abspath(self.log_path)), exist_ok=True)
                with open(self.log_path, "a", encoding="utf-8") as f:
                    f.write(line + "\n")
            except Exception:
                pass  # Never crash on logging failure

    def info(self,  step: str, code: str, msg: str): self._write("INFO",  step, code, msg)
    def warn(self,  step: str, code: str, msg: str): self._write("WARN",  step, code, msg)
    def error(self, step: str, code: str, msg: str): self._write("ERROR", step, code, msg)
    def debug(self, step: str, code: str, msg: str): self._write("DEBUG", step, code, msg)


# ═════════════════════════════════════════════════════════════════════════════
# CircuitBreaker — per-step failure tracking
# ═════════════════════════════════════════════════════════════════════════════
class CircuitBreaker:
    """
    Per-step circuit breaker. Opens after N failures, recovers after timeout.
    State is in-memory (resets on process restart — intentional for daily ops).
    """

    def __init__(self):
        self._failures: Dict[str, int] = {}
        self._opened_at: Dict[str, float] = {}

    def is_open(self, step: str) -> bool:
        cfg = CIRCUIT_BREAKER_THRESHOLDS.get(step, {"failures": 5, "recovery_seconds": 300})
        failures = self._failures.get(step, 0)
        if failures < cfg["failures"]:
            return False
        opened = self._opened_at.get(step, 0)
        if time.monotonic() - opened > cfg["recovery_seconds"]:
            self._failures[step] = 0  # Auto-reset after recovery window
            return False
        return True

    def time_until_recovery(self, step: str) -> int:
        cfg = CIRCUIT_BREAKER_THRESHOLDS.get(step, {"recovery_seconds": 300})
        opened = self._opened_at.get(step, 0)
        remaining = cfg["recovery_seconds"] - (time.monotonic() - opened)
        return max(0, int(remaining))

    def record_failure(self, step: str):
        self._failures[step] = self._failures.get(step, 0) + 1
        if self._failures[step] == CIRCUIT_BREAKER_THRESHOLDS.get(
            step, {"failures": 5}
        )["failures"]:
            self._opened_at[step] = time.monotonic()

    def record_success(self, step: str):
        self._failures[step] = 0
        self._opened_at.pop(step, None)


# ═════════════════════════════════════════════════════════════════════════════
# OperationHandler — wraps any function with retry + circuit breaker + taxonomy
# ═════════════════════════════════════════════════════════════════════════════
class OperationHandler:
    """
    Wraps operations with:
    - Taxonomy error code classification
    - Exponential backoff retry (skipped for non-retryable codes)
    - Circuit breaker per step
    - Structured timing

    Returns: (success, result, error_code, error_message, duration_seconds)
    """

    def __init__(self, logger: OpsLogger, circuit_breaker: CircuitBreaker):
        self.logger = logger
        self.cb = circuit_breaker
        self.retry_delays = [1, 2, 4]

    def classify_error(self, exc: Exception) -> str:
        msg = str(exc).lower()
        for pattern, code in ERROR_CODE_MAP.items():
            if pattern in msg:
                return code
        # Fallback by exception type
        if isinstance(exc, TimeoutError):
            return "GH_004"
        if isinstance(exc, PermissionError):
            return "BR_001"
        if isinstance(exc, ConnectionError):
            return "GH_004"
        return "UNKNOWN"

    def execute(
        self,
        step: str,
        func: Callable,
        *args,
        **kwargs,
    ) -> Tuple[bool, Any, Optional[str], Optional[str], float]:
        """
        Execute func with retry + circuit breaker.
        Returns: (success, result, error_code, error_message, duration_seconds)
        """
        start = time.monotonic()

        # Circuit breaker check
        if self.cb.is_open(step):
            recovery = self.cb.time_until_recovery(step)
            code = f"{step.upper()[:2]}_CIRCUIT_OPEN"
            msg = f"Circuit breaker OPEN — recovery in {recovery}s"
            self.logger.warn(step, code, msg)
            return False, None, code, msg, time.monotonic() - start

        last_code = "UNKNOWN"
        last_msg = ""

        for attempt in range(len(self.retry_delays) + 1):
            try:
                result = func(*args, **kwargs)
                self.cb.record_success(step)
                duration = round(time.monotonic() - start, 2)
                self.logger.info(step, "OK_000", f"✅ Completed in {duration}s")
                return True, result, None, None, duration

            except Exception as exc:
                last_code = self.classify_error(exc)
                last_msg = str(exc)
                self.cb.record_failure(step)

                is_last = attempt == len(self.retry_delays)
                is_non_retryable = last_code in NON_RETRYABLE

                if is_non_retryable:
                    self.logger.error(step, last_code, f"❌ Non-retryable: {last_msg}")
                    break

                if is_last:
                    self.logger.error(step, last_code, f"❌ All retries exhausted: {last_msg}")
                    break

                delay = self.retry_delays[attempt]
                self.logger.warn(
                    step, last_code,
                    f"⚠️ Attempt {attempt + 1} failed ({last_msg[:80]}). Retrying in {delay}s..."
                )
                time.sleep(delay)

        duration = round(time.monotonic() - start, 2)
        return False, None, last_code, last_msg, duration


# ═════════════════════════════════════════════════════════════════════════════
# APIClient — base HTTP client with rate limiting
# ═════════════════════════════════════════════════════════════════════════════
class RateLimitError(Exception):
    pass


class APIClient:
    def __init__(self, requests_per_second: float = 1.0):
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
                    body = response.read()
                    if body:
                        try:
                            return json.loads(body.decode("utf-8"))
                        except json.JSONDecodeError:
                            return body.decode("utf-8")
                    return None
            except urllib_error.HTTPError as e:
                self.last_request_time = time.monotonic()
                if e.code == 429:
                    wait = 2 ** attempt
                    if attempt == retries - 1:
                        raise RateLimitError(f"HTTP 429 Too Many Requests from {url}.") from e
                    time.sleep(wait)
                    continue
                if e.code >= 500:
                    wait = 2 ** attempt
                    if attempt == retries - 1:
                        raise RuntimeError(f"Server error {e.code} from {url}.") from e
                    time.sleep(wait)
                    continue
                try:
                    body = e.read().decode("utf-8", errors="replace")[:1000]
                except OSError:
                    body = e.reason
                raise RuntimeError(f"HTTP {e.code} from {url}: {body}") from e
            except urllib_error.URLError as e:
                if attempt == retries - 1:
                    raise RuntimeError(f"Failed to connect to {url}: {e}") from e
                time.sleep(2 ** attempt)


# ═════════════════════════════════════════════════════════════════════════════
# Helpers
# ═════════════════════════════════════════════════════════════════════════════
def write_json(data: dict, path: str):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _get_ops_log_dir() -> str:
    vault = os.environ.get("VAULT_PATH", ".")
    return os.path.join(vault, "Ops-Logs")


def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _now_iso() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _session_id() -> str:
    return f"ops_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


# ═════════════════════════════════════════════════════════════════════════════
# Step functions (original logic preserved, now return structured dicts)
# ═════════════════════════════════════════════════════════════════════════════
def _do_health_check(logger: OpsLogger) -> dict:
    client = APIClient()
    logger.info("health_check", "HC_000", "Starting health check...")

    # Docker daemon check
    try:
        result = subprocess.run(
            ["docker", "info"], capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            raise RuntimeError("Docker daemon not responding")
        logger.info("health_check", "HC_000", "Docker daemon ✅ responding")
    except FileNotFoundError:
        raise RuntimeError("docker daemon not responding — Docker not found in PATH")

    # Container check
    try:
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.Status}}", "hyper-brain"],
            capture_output=True, text=True, timeout=10
        )
        container_status = result.stdout.strip()
        if container_status != "running":
            raise RuntimeError(f"hyper-brain container status: {container_status}")
        uptime_result = subprocess.run(
            ["docker", "inspect", "--format",
             "{{.State.StartedAt}}", "hyper-brain"],
            capture_output=True, text=True, timeout=10
        )
        logger.info("health_check", "HC_000",
                    f"hyper-brain container ✅ running (started: {uptime_result.stdout.strip()[:19]})")
    except Exception as e:
        raise RuntimeError(f"hyper-brain {e}") from e

    # API check
    start = time.monotonic()
    resp = client._request("http://localhost:8100/health", retries=1)
    api_ms = round((time.monotonic() - start) * 1000)
    if api_ms > 5000:
        raise TimeoutError(f"Briefing API timeout ({api_ms}ms > 5000ms)")
    logger.info("health_check", "HC_000", f"Briefing API ✅ responding (200 OK, {api_ms}ms)")

    return {
        "docker_daemon": "✅ responding",
        "hyper_brain_container": "✅ running",
        "briefing_api": f"✅ responding (200 OK, {api_ms}ms)",
        "api_response": resp,
    }


def _do_github_sync(logger: OpsLogger) -> dict:
    token = os.environ.get("GITHUB_PAT")
    if not token:
        raise RuntimeError("token invalid — GITHUB_PAT not set")

    vault_path = os.environ.get("VAULT_PATH")
    if not vault_path:
        raise RuntimeError("vault path not set — VAULT_PATH missing")

    inbox_dir = os.path.join(vault_path, "GitHub-Inbox")
    os.makedirs(inbox_dir, exist_ok=True)

    client = APIClient(requests_per_second=2)
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    synced, failed_repos, total_issues = [], [], 0

    for repo in REPOS:
        url = f"https://api.github.com/repos/{repo}/issues?state=open&per_page=50"
        try:
            issues = client._request(url, headers=headers)
            issues = [i for i in (issues or []) if "pull_request" not in i]
            repo_name = repo.split("/")[1]
            total_issues += len(issues)

            date_str = _today()
            lines = [
                f"# 🐛 {repo_name} — Open Issues\n",
                f"*Synced: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n",
                f"*Total: {len(issues)} open issues*\n",
                "---\n",
            ]
            if not issues:
                lines.append("✅ No open issues. BROski clean!\n")
            else:
                for issue in issues:
                    assignee = (issue.get("assignee") or {}).get("login", "unassigned")
                    labels = ", ".join(l["name"] for l in issue.get("labels", [])) or "none"
                    lines += [
                        f"- [ ] #{issue['number']} — {issue['title']}",
                        f"  - 🔗 {issue['html_url']}",
                        f"  - 👤 {assignee} | 🏷️ {labels}",
                        "",
                    ]

            out_file = os.path.join(inbox_dir, f"{date_str}-{repo_name}.md")
            with open(out_file, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

            logger.info("github_sync", "GH_000", f"✅ {repo_name}: {len(issues)} issues synced")
            synced.append({"repo": repo_name, "issues": len(issues), "file": out_file})

        except RateLimitError as e:
            logger.warn("github_sync", "GH_002", f"Rate limit hit for {repo}: {e}")
            failed_repos.append({"repo": repo, "error_code": "GH_002", "reason": str(e)})
        except Exception as e:
            code = "GH_003" if ("403" in str(e) or "404" in str(e) or "no access" in str(e).lower()) else "GH_004"
            logger.warn("github_sync", code, f"Failed {repo}: {e}")
            failed_repos.append({"repo": repo, "error_code": code, "reason": str(e)})

    if not synced and failed_repos:
        raise RuntimeError(f"no access — all {len(failed_repos)} repos failed to sync")

    return {
        "repos_attempted": len(REPOS),
        "repos_succeeded": len(synced),
        "repos_failed": len(failed_repos),
        "issues_synced": total_issues,
        "failed_repos": failed_repos,
    }


def _do_generate_briefing(logger: OpsLogger) -> dict:
    vault_path = os.environ.get("VAULT_PATH")
    if not vault_path:
        raise RuntimeError("vault path does not exist — VAULT_PATH not set")

    briefings_dir = os.path.join(vault_path, "Briefings")
    try:
        os.makedirs(briefings_dir, exist_ok=True)
    except Exception as e:
        raise RuntimeError(f"briefings — could not create Briefings/ folder: {e}") from e

    logger.info("briefing_generation", "BR_000", "Triggering briefing API...")
    client = APIClient()
    resp = client._request("http://localhost:8100/briefing/generate", method="POST")

    date_str = _today()
    out_file = os.path.join(briefings_dir, f"{date_str}-briefing.md")

    content = resp if isinstance(resp, str) else json.dumps(resp, indent=2)
    if not content:
        content = f"# 🧠 Briefing — {date_str}\n\n*No content returned from API.*\n"

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(content)

    size = os.path.getsize(out_file)
    sections = content.count("\n## ") + content.count("\n# ")
    logger.info("briefing_generation", "BR_000",
                f"✅ Written: {out_file} ({size} bytes, ~{sections} sections)")

    return {
        "file_path": out_file,
        "file_size_bytes": size,
        "sections_generated": sections,
        "sections_skipped": 0,
    }


def _do_vault_commit(logger: OpsLogger) -> dict:
    vault_path = os.environ.get("VAULT_PATH", ".")
    date_str = _today()
    commit_msg = f"ops: sync briefings and github inbox {_now_iso()}"

    logger.info("vault_commit", "VC_000", f"Committing vault changes in {vault_path}...")

    # Check git is initialised
    git_dir = os.path.join(vault_path, ".git")
    if not os.path.exists(git_dir):
        raise RuntimeError("git not initialized in vault folder")

    # Check for changes
    status = subprocess.run(
        ["git", "-C", vault_path, "status", "--porcelain"],
        capture_output=True, text=True, timeout=30
    )
    if not status.stdout.strip():
        logger.info("vault_commit", "VC_000", "⏭️ No changes to commit")
        return {"status": "NO_CHANGES", "commit_hash": None, "files_changed": 0}

    # Stage all
    subprocess.run(
        ["git", "-C", vault_path, "add", "--all"],
        check=True, capture_output=True, timeout=30
    )

    # Commit
    commit = subprocess.run(
        ["git", "-C", vault_path, "commit", "-m", commit_msg],
        capture_output=True, text=True, timeout=30
    )
    if commit.returncode != 0:
        raise RuntimeError(f"merge conflict? git commit failed: {commit.stderr[:200]}")

    # Get hash
    hash_result = subprocess.run(
        ["git", "-C", vault_path, "rev-parse", "--short", "HEAD"],
        capture_output=True, text=True, timeout=10
    )
    commit_hash = hash_result.stdout.strip()

    # Count files
    files_changed = len(status.stdout.strip().splitlines())
    logger.info("vault_commit", "VC_000",
                f"✅ Committed {commit_hash} — {files_changed} files changed")

    return {
        "status": "COMMITTED",
        "commit_hash": commit_hash,
        "commit_message": commit_msg,
        "files_changed": files_changed,
    }


def _do_discord_report(logger: OpsLogger, status_obj: dict) -> dict:
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        raise RuntimeError("webhook URL invalid — DISCORD_WEBHOOK_URL not set")

    summary = status_obj.get("summary", {})
    steps = status_obj.get("steps", {})

    def step_line(key: str, label: str) -> str:
        s = steps.get(key, {})
        icon = "✅" if s.get("status") in ("HEALTHY", "GENERATED", "COMMITTED", "FULL", "SENT", "NO_CHANGES") else (
               "⚠️" if s.get("status") in ("DEGRADED", "PARTIAL", "UNCOMMITTED") else "❌")
        detail = s.get("error_message") or s.get("status", "—")
        dur = s.get("duration_seconds", 0)
        return f"{icon} **{label}** — {detail} `({dur}s)`"

    fields = [
        {"name": "🐳 Health Check",    "value": step_line("health_check",        "Health"),   "inline": False},
        {"name": "🐙 GitHub Sync",     "value": step_line("github_sync",         "GitHub"),   "inline": False},
        {"name": "📝 Briefing",         "value": step_line("briefing_generation", "Briefing"), "inline": False},
        {"name": "💾 Vault Commit",     "value": step_line("vault_commit",        "Vault"),    "inline": False},
    ]

    # Next steps if errors
    next_steps = summary.get("next_steps", [])
    if next_steps:
        fields.append({
            "name": "⚠️ Action Required",
            "value": "\n".join(f"• {s}" for s in next_steps[:5]),
            "inline": False,
        })

    overall = summary.get("overall_status", "UNKNOWN")
    colour = 0x2ECC71 if overall == "HEALTHY" else (0xF39C12 if overall == "PARTIAL" else 0xE74C3C)

    payload = {
        "embeds": [{
            "title": f"🧠 BROski Brain Ops — {_today()}",
            "description": summary.get("message", "Morning ops complete."),
            "color": colour,
            "fields": fields,
            "footer": {"text": f"BROski♾️ v{OPS_VERSION} | session: {status_obj.get('session_id', '—')}"},
            "timestamp": _now_iso(),
        }]
    }

    client = APIClient()
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json", "User-Agent": "HyperBrainOps/2.0"}
    resp = client._request(webhook_url, method="POST", headers=headers, data=data)
    logger.info("discord_report", "DC_000", "✅ Discord report sent")
    return {"channel": "brain-ops", "message_sent": True}


# ═════════════════════════════════════════════════════════════════════════════
# Canonical status builder
# ═════════════════════════════════════════════════════════════════════════════
def build_status_object(session_id: str, step_results: dict) -> dict:
    """
    Assembles the canonical ops-status.json from individual step results.
    step_results: {step_name: (success, result, error_code, error_msg, duration)}
    """
    steps_out = {}
    all_ok = True
    has_partial = False
    errors_for_summary = []

    STATUS_MAP = {
        "health_check":        ("HEALTHY",   "UNHEALTHY"),
        "github_sync":         ("FULL",      "FAILED"),
        "briefing_generation": ("GENERATED", "FAILED"),
        "vault_commit":        ("COMMITTED", "UNCOMMITTED"),
        "discord_report":      ("SENT",      "FAILED"),
    }

    for step, (success, result, error_code, error_msg, duration) in step_results.items():
        ok_status, fail_status = STATUS_MAP.get(step, ("OK", "FAILED"))

        # Special cases
        if step == "vault_commit" and success and isinstance(result, dict):
            status = result.get("status", ok_status)
        elif step == "github_sync" and success and isinstance(result, dict):
            failed = result.get("repos_failed", 0)
            status = "PARTIAL" if failed > 0 else "FULL"
            if failed > 0:
                has_partial = True
        else:
            status = ok_status if success else fail_status

        if not success:
            all_ok = False
            if error_code and error_code not in ("SKIPPED",):
                errors_for_summary.append({"code": error_code, "msg": error_msg})

        steps_out[step] = {
            "status": status,
            "duration_seconds": duration,
            "details": result if isinstance(result, dict) else {},
            "error_code": error_code,
            "error_message": error_msg,
        }

    overall = "HEALTHY" if all_ok and not has_partial else ("PARTIAL" if has_partial or (not all_ok) else "FAILED")
    icon = "✅" if overall == "HEALTHY" else ("⚠️" if overall == "PARTIAL" else "❌")

    next_steps = []
    for err in errors_for_summary:
        code = err["code"]
        action_map = {
            "GH_001": "Regenerate GitHub PAT at github.com/settings/tokens",
            "GH_002": "Wait 1h then re-run sync-github",
            "GH_003": "Check GITHUB_REPOS env var + PAT scopes",
            "GH_004": "Check internet connection, retry",
            "DC_001": "Regenerate webhook in Discord server settings",
            "DC_002": "Check webhook channel permissions",
            "VC_001": "Run: cd $VAULT_PATH && git init",
            "VC_002": "Run: git config user.name 'BROski' && git config user.email '...'",
            "BR_001": "Check VAULT_PATH exists and is writable",
            "HC_001": "Restart Docker Desktop",
            "HC_002": "Run: docker logs hyper-brain",
        }
        if code in action_map:
            next_steps.append(f"{code}: {action_map[code]}")

    summary_msg = "All systems go. Fresh briefing in vault. 🧠" if all_ok and not has_partial else (
        f"Ops complete with warnings. {len(errors_for_summary)} issue(s) need attention."
        if has_partial else
        f"Ops encountered errors. {len(errors_for_summary)} step(s) failed."
    )

    return {
        "timestamp": _now_iso(),
        "session_id": session_id,
        "ops_version": OPS_VERSION,
        "steps": steps_out,
        "summary": {
            "overall_status": overall,
            "icon": icon,
            "message": summary_msg,
            "next_steps": next_steps,
            "all_ok": all_ok and not has_partial,
            "total_duration_seconds": round(sum(v[4] for v in step_results.values()), 2),
        },
    }


def write_obsidian_dashboard(status_obj: dict, vault_path: str):
    """Writes the daily Obsidian dashboard note to Ops-Logs/."""
    date_str = _today()
    ops_dir = os.path.join(vault_path, "Ops-Logs")
    os.makedirs(ops_dir, exist_ok=True)

    summary = status_obj["summary"]
    steps = status_obj["steps"]

    def row(label: str, key: str, detail_key: str = None) -> str:
        s = steps.get(key, {})
        icon = "✅" if s.get("status") in ("HEALTHY", "GENERATED", "COMMITTED", "FULL", "SENT", "NO_CHANGES") else (
               "⚠️" if s.get("status") in ("DEGRADED", "PARTIAL") else "❌")
        detail = ""
        if detail_key and isinstance(s.get("details"), dict):
            detail = str(s["details"].get(detail_key, s.get("status", "—")))
        else:
            detail = s.get("status", "—")
        dur = s.get("duration_seconds", 0)
        return f"| {label} | {icon} {s.get('status', '—')} | {detail} ({dur}s) |"

    errors_section = ""
    for step_name, step_data in steps.items():
        if step_data.get("error_code"):
            errors_section += (
                f"\n- **{step_data['error_code']}** ({step_name}): "
                f"{step_data.get('error_message', '—')}\n"
            )
    if not errors_section:
        errors_section = "\n✅ No errors. Clean run!\n"

    dashboard = f"""---
tags: [ops, daily-status, brain-ops]
date: {date_str}
session_id: {status_obj['session_id']}
overall_status: {summary['overall_status']}
---

# 🧠 Brain Ops Status — {date_str}

**Status:** {summary['icon']} {summary['overall_status']} — {summary['message']}

---

## ⚡ Quick Summary

| Component | Status | Detail |
|---|---|---|
{row("🐳 Health Check",    "health_check",        "briefing_api")}
{row("🔗 GitHub Sync",     "github_sync",         "issues_synced")}
{row("📝 Briefing",         "briefing_generation", "file_size_bytes")}
{row("💾 Vault Commit",     "vault_commit",        "commit_hash")}
{row("💬 Discord Report",   "discord_report",      "channel")}

---

## 🔴 Errors & Next Steps
{errors_section}
{chr(10).join(f"- ✅ Action: `{s}`" for s in summary.get("next_steps", [])) or "_No actions needed._"}

---

## 📊 Timing

| Step | Duration |
|---|---|
| Health Check | {steps.get("health_check", {}).get("duration_seconds", 0)}s |
| GitHub Sync | {steps.get("github_sync", {}).get("duration_seconds", 0)}s |
| Briefing Gen | {steps.get("briefing_generation", {}).get("duration_seconds", 0)}s |
| Vault Commit | {steps.get("vault_commit", {}).get("duration_seconds", 0)}s |
| Discord | {steps.get("discord_report", {}).get("duration_seconds", 0)}s |
| **Total** | **{summary.get("total_duration_seconds", 0)}s** |

---

## 🔍 Agent-Readable Status

```json
{json.dumps({"session_id": status_obj["session_id"], "overall_status": summary["overall_status"], "all_ok": summary["all_ok"], "errors": [{"code": s.get("error_code"), "step": k} for k, s in steps.items() if s.get("error_code")]}, indent=2)}
```

---

## 🔗 Links

- [[Briefings/{date_str}-briefing|📋 Today's Briefing]]
- [[GitHub-Inbox/{date_str}-github-sync-report|🔗 GitHub Sync Report]]
- [[Ops-Logs/{date_str}-ops.log|📜 Full Ops Log]]

---
_Generated by BROski Brain Ops v{OPS_VERSION}_
"""

    out_file = os.path.join(ops_dir, f"{date_str}-dashboard.md")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(dashboard)

    status_file = os.path.join(ops_dir, f"{date_str}-ops-status.json")
    write_json(status_obj, status_file)

    return out_file, status_file


# ═════════════════════════════════════════════════════════════════════════════
# CLI subcommand handlers
# ═════════════════════════════════════════════════════════════════════════════
def fix_env(args):
    print("🔍 Checking Environment...")
    issues = []
    for var in ("GITHUB_PAT", "DISCORD_WEBHOOK_URL", "VAULT_PATH"):
        val = os.environ.get(var)
        if not val:
            issues.append(f"❌ {var} is missing")
        elif var == "VAULT_PATH" and not os.path.exists(val):
            issues.append(f"❌ VAULT_PATH does not exist: {val}")
        else:
            print(f"✅ {var} is set{(' → ' + val) if var == 'VAULT_PATH' else ''}")
    if issues:
        print("\n".join(issues))
        sys.exit(1)
    print("🚀 Environment is ready!")


def check_health(args):
    log_path = os.path.join(_get_ops_log_dir(), f"{_today()}-ops.log") if os.environ.get("VAULT_PATH") else None
    logger = OpsLogger(log_path=log_path)
    cb = CircuitBreaker()
    handler = OperationHandler(logger, cb)
    success, result, code, msg, dur = handler.execute("health_check", _do_health_check, logger)
    if not success and getattr(args, "restart_if_down", False):
        print("🔄 Attempting container restart...")
        try:
            subprocess.run(["docker", "restart", "hyper-brain"], check=True)
            print("✅ Restarted hyper-brain.")
        except Exception as e:
            print(f"❌ Restart failed: {e}")
    if args.output:
        write_json({"status": "healthy" if success else "unhealthy", "error_code": code, "details": result or {}}, args.output)


def generate_briefing(args):
    log_path = os.path.join(_get_ops_log_dir(), f"{_today()}-ops.log") if os.environ.get("VAULT_PATH") else None
    logger = OpsLogger(log_path=log_path)
    cb = CircuitBreaker()
    handler = OperationHandler(logger, cb)
    success, result, code, msg, dur = handler.execute("briefing_generation", _do_generate_briefing, logger)
    if args.output:
        write_json({"status": "success" if success else "error", "error_code": code, "details": result or {}}, args.output)


def sync_github(args):
    log_path = os.path.join(_get_ops_log_dir(), f"{_today()}-ops.log") if os.environ.get("VAULT_PATH") else None
    logger = OpsLogger(log_path=log_path)
    cb = CircuitBreaker()
    handler = OperationHandler(logger, cb)
    success, result, code, msg, dur = handler.execute("github_sync", _do_github_sync, logger)
    if args.output:
        write_json({"status": "success" if success else "error", "error_code": code, "details": result or {}}, args.output)


def send_report(args):
    """Legacy single-step report. Prefer run-all for canonical output."""
    log_path = os.path.join(_get_ops_log_dir(), f"{_today()}-ops.log") if os.environ.get("VAULT_PATH") else None
    logger = OpsLogger(log_path=log_path)
    cb = CircuitBreaker()
    handler = OperationHandler(logger, cb)

    # Build minimal status from output files if they exist
    status_obj = {"session_id": _session_id(), "steps": {}, "summary": {"overall_status": "UNKNOWN", "message": "Legacy report.", "next_steps": [], "all_ok": False}}
    output_dir = "output"
    for fname, step in (("health.json", "health_check"), ("briefing.json", "briefing_generation"), ("sync.json", "github_sync")):
        fpath = os.path.join(output_dir, fname)
        if os.path.exists(fpath):
            try:
                with open(fpath, encoding="utf-8") as f:
                    d = json.load(f)
                status_obj["steps"][step] = {"status": d.get("status", "UNKNOWN"), "duration_seconds": 0, "details": d, "error_code": d.get("error_code"), "error_message": None}
            except Exception:
                pass

    success, result, code, msg, dur = handler.execute("discord_report", _do_discord_report, logger, status_obj)
    if not success:
        print(f"❌ Discord report failed: {code} — {msg}")


def run_all(args):
    """
    Full ops chain. Writes canonical ops-status.json + Obsidian dashboard.
    Stops chain if health_check fails.
    """
    session_id = _session_id()
    vault_path = os.environ.get("VAULT_PATH", ".")
    log_path = os.path.join(vault_path, "Ops-Logs", f"{_today()}-ops.log")

    logger = OpsLogger(log_path=log_path)
    cb = CircuitBreaker()
    handler = OperationHandler(logger, cb)

    logger.info("run_all", "OPS_000", f"🚀 BROski Brain Ops v{OPS_VERSION} — session {session_id}")

    step_results = {}
    SKIPPED = (False, None, "SKIPPED", "Step skipped", 0.0)

    # ── Step 1: Health Check (chain-stopper) ─────────────────────────────────
    r = handler.execute("health_check", _do_health_check, logger)
    step_results["health_check"] = r
    if not r[0]:  # Failed
        logger.error("run_all", "HC_CHAIN_STOP", "❌ Health check failed — halting ops chain")
        for step in ("github_sync", "briefing_generation", "vault_commit", "discord_report"):
            step_results[step] = SKIPPED

        status_obj = build_status_object(session_id, step_results)
        status_obj["summary"]["message"] = "HALTED: Docker/API down. No operations ran."
        if vault_path:
            write_obsidian_dashboard(status_obj, vault_path)
        print(json.dumps(status_obj["summary"], indent=2, ensure_ascii=False))
        sys.exit(1)

    # ── Step 2: GitHub Sync ───────────────────────────────────────────────────
    step_results["github_sync"] = handler.execute("github_sync", _do_github_sync, logger)

    # ── Step 3: Briefing Generation ───────────────────────────────────────────
    step_results["briefing_generation"] = handler.execute(
        "briefing_generation", _do_generate_briefing, logger
    )

    # ── Step 4: Vault Commit ──────────────────────────────────────────────────
    step_results["vault_commit"] = handler.execute("vault_commit", _do_vault_commit, logger)

    # ── Build canonical status ────────────────────────────────────────────────
    status_obj = build_status_object(session_id, step_results)

    # ── Step 5: Discord Report ────────────────────────────────────────────────
    step_results["discord_report"] = handler.execute(
        "discord_report", _do_discord_report, logger, status_obj
    )
    # Rebuild with discord result included
    status_obj = build_status_object(session_id, step_results)

    # ── Write outputs ─────────────────────────────────────────────────────────
    if vault_path:
        dashboard_file, status_file = write_obsidian_dashboard(status_obj, vault_path)
        logger.info("run_all", "OPS_000", f"📊 Dashboard: {dashboard_file}")
        logger.info("run_all", "OPS_000", f"📄 Status JSON: {status_file}")

    logger.info("run_all", "OPS_000",
                f"{'✅' if status_obj['summary']['all_ok'] else '⚠️'} "
                f"Done — {status_obj['summary']['overall_status']} "
                f"({status_obj['summary']['total_duration_seconds']}s total)")

    print(json.dumps(status_obj["summary"], indent=2, ensure_ascii=False))


# ═════════════════════════════════════════════════════════════════════════════
# CLI entry point
# ═════════════════════════════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(
        description=f"🧠 BROski Brain Ops v{OPS_VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  fix-env             Check required env vars + paths
  check-health        Verify Docker + hyper-brain + API
  generate-briefing   Trigger morning briefing
  sync-github         Sync open issues into vault
  report              Send Discord status (legacy)
  run-all             Full ops chain + canonical output  ← USE THIS
        """,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("fix-env", help="Check environment variables")

    p_health = sub.add_parser("check-health", help="Check container health")
    p_health.add_argument("--output", help="Output JSON path")
    p_health.add_argument("--restart-if-down", action="store_true")

    p_brief = sub.add_parser("generate-briefing", help="Trigger morning briefing")
    p_brief.add_argument("--output", help="Output JSON path")

    p_sync = sub.add_parser("sync-github", help="Sync GitHub issues to vault")
    p_sync.add_argument("--output", help="Output JSON path")

    sub.add_parser("report", help="Send Discord report (legacy — prefer run-all)")

    sub.add_parser("run-all", help="🚀 Full ops chain with canonical status output")

    args = parser.parse_args()
    {
        "fix-env":            fix_env,
        "check-health":       check_health,
        "generate-briefing":  generate_briefing,
        "sync-github":        sync_github,
        "report":             send_report,
        "run-all":            run_all,
    }[args.command](args)


if __name__ == "__main__":
    main()
