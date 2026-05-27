#!/usr/bin/env python3
"""
github_to_obsidian_v2.py
HYPER-UPGRADED: Async parallel fetching + resilience + type safety

Pulls open issues from all 4 welshDog repos → Obsidian vault in ~2s (was ~10s).
Run every 4hrs via Docker cron or manually.

BROski♾️ → BROSKI⚡♾️
"""

import asyncio
import aiohttp
import os
from datetime import datetime
from typing import TypedDict, Optional, List
from dataclasses import dataclass, field
from enum import Enum
import logging

# ========== TYPE DEFINITIONS ==========

class GithubIssue(TypedDict, total=False):
    """GitHub API issue response schema"""
    number: int
    title: str
    html_url: str
    assignee: Optional[dict]
    labels: List[dict]
    pull_request: Optional[dict]


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Stop requests (too many failures)
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class RetryConfig:
    """Exponential backoff configuration"""
    max_retries: int = 3
    base_delay_ms: int = 100
    max_delay_ms: int = 5000
    backoff_multiplier: float = 2.0

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for attempt (0-indexed)"""
        delay_ms = min(
            self.base_delay_ms * (self.backoff_multiplier ** attempt),
            self.max_delay_ms
        )
        return delay_ms / 1000.0


@dataclass
class CircuitBreaker:
    """Circuit breaker: stops hammering on repeated failures"""
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = 0
    failure_threshold: int = 5
    recovery_timeout_sec: int = 60
    last_failure_time: Optional[float] = None

    def record_success(self) -> None:
        """Reset on success"""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0

    def record_failure(self) -> None:
        """Increment failures, open circuit if threshold exceeded"""
        self.failure_count += 1
        self.last_failure_time = datetime.now().timestamp()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.warning(f"🚪 Circuit breaker OPENED after {self.failure_count} failures")

    def can_proceed(self) -> bool:
        """Check if we should proceed with request"""
        if self.state == CircuitBreakerState.CLOSED:
            return True
        elif self.state == CircuitBreakerState.OPEN:
            # Check if recovery timeout has passed
            if self.last_failure_time:
                elapsed = datetime.now().timestamp() - self.last_failure_time
                if elapsed > self.recovery_timeout_sec:
                    self.state = CircuitBreakerState.HALF_OPEN
                    logger.info("🔄 Circuit breaker in HALF_OPEN (testing recovery)...")
                    return True
            return False
        else:  # HALF_OPEN
            return True


@dataclass
class SyncResult:
    """Result of syncing a single repo"""
    repo_name: str
    success: bool
    issue_count: int = 0
    duration_ms: float = 0.0
    error_msg: Optional[str] = None


@dataclass
class SyncSummary:
    """Overall sync summary"""
    total_repos: int
    synced_repos: int
    failed_repos: int
    total_issues: int
    total_duration_ms: float
    results: List[SyncResult] = field(default_factory=list)

# ========== LOGGING SETUP ==========

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# ========== CONFIGURATION ==========

GITHUB_TOKEN = os.environ.get("GITHUB_PAT", "")
VAULT_PATH = os.environ.get(
    "OBSIDIAN_VAULT_PATH",
    r"C:\Users\Lyndz\Obsidian\HYPERFOCUS_ZONE\00-Inbox\GitHub"
)
REPOS = [
    "welshDog/HyperCode-V2.4",
    "welshDog/HyperAgent-SDK",
    "welshDog/BROskiPets-LLM-dNFT",
    "welshDog/Hyper-Vibe-Coding-Course"
]

RETRY_CONFIG = RetryConfig()
CIRCUIT_BREAKER = CircuitBreaker()

# ========== CORE FUNCTIONS ==========

def validate_config() -> None:
    """Validate required environment variables"""
    if not GITHUB_TOKEN:
        logger.error("❌ GITHUB_PAT not set. Export it first.")
        exit(1)
    os.makedirs(VAULT_PATH, exist_ok=True)
    logger.info(f"✅ Config validated. Vault: {VAULT_PATH}")


async def fetch_issues_with_retry(
    session: aiohttp.ClientSession,
    repo: str,
    retry_config: RetryConfig = RETRY_CONFIG
) -> tuple[Optional[List[GithubIssue]], Optional[str]]:
    """
    Fetch issues with exponential backoff retry.
    Returns (issues, error_msg)
    """
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"https://api.github.com/repos/{repo}/issues?state=open&per_page=50"

    for attempt in range(retry_config.max_retries):
        try:
            async with session.get(url, headers=headers, timeout=10) as resp:
                # Check rate limit headers
                remaining = resp.headers.get("X-RateLimit-Remaining", "?")
                
                if resp.status == 200:
                    data = await resp.json()
                    # Filter out PRs
                    issues = [i for i in data if "pull_request" not in i]
                    logger.info(f"🟢 Fetched {repo}: {len(issues)} issues (rate: {remaining} remaining)")
                    CIRCUIT_BREAKER.record_success()
                    return issues, None

                elif resp.status == 429:
                    # Rate limited
                    retry_after = int(resp.headers.get("Retry-After", "60"))
                    msg = f"⏳ {repo}: Rate limited (429). Retrying in {retry_after}s (attempt {attempt + 1}/{retry_config.max_retries})"
                    logger.warning(msg)
                    await asyncio.sleep(retry_after)
                    continue

                elif resp.status == 404:
                    msg = f"❌ {repo}: Not found (404)"
                    logger.error(msg)
                    CIRCUIT_BREAKER.record_failure()
                    return None, msg

                else:
                    msg = f"❌ {repo}: HTTP {resp.status}"
                    logger.error(msg)
                    CIRCUIT_BREAKER.record_failure()
                    return None, msg

        except asyncio.TimeoutError:
            msg = f"⏳ {repo}: Timeout. Attempt {attempt + 1}/{retry_config.max_retries}"
            logger.warning(msg)
            if attempt < retry_config.max_retries - 1:
                delay = retry_config.get_delay(attempt)
                await asyncio.sleep(delay)

        except Exception as e:
            msg = f"❌ {repo}: {str(e)}"
            logger.error(msg)
            CIRCUIT_BREAKER.record_failure()
            return None, msg

    return None, f"Failed after {retry_config.max_retries} retries"


def format_markdown(repo_name: str, issues: List[GithubIssue]) -> str:
    """Format issues as Markdown"""
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

    return "\n".join(lines)


def write_vault_file(repo_name: str, markdown: str) -> None:
    """Write Markdown file to vault"""
    out_file = os.path.join(VAULT_PATH, f"{repo_name}.md")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(markdown)


async def sync_repo(
    session: aiohttp.ClientSession,
    repo: str
) -> SyncResult:
    """Sync single repo: fetch → format → write"""
    start = datetime.now()
    repo_name = repo.split("/")[1]

    # Check circuit breaker
    if not CIRCUIT_BREAKER.can_proceed():
        msg = f"🚪 {repo}: Circuit breaker OPEN"
        logger.warning(msg)
        return SyncResult(repo_name, False, error_msg=msg)

    # Fetch issues
    issues, error = await fetch_issues_with_retry(session, repo)
    if error:
        return SyncResult(repo_name, False, error_msg=error)

    if issues is None:
        return SyncResult(repo_name, False, error_msg="No issues returned")

    # Format + write
    try:
        markdown = format_markdown(repo_name, issues)
        write_vault_file(repo_name, markdown)
        duration = (datetime.now() - start).total_seconds() * 1000
        logger.info(f"✅ Synced {repo_name}: {len(issues)} issues ({duration:.0f}ms)")
        return SyncResult(repo_name, True, len(issues), duration)
    except Exception as e:
        msg = f"Error writing {repo_name}: {str(e)}"
        logger.error(msg)
        return SyncResult(repo_name, False, error_msg=msg)


async def sync_all_repos() -> SyncSummary:
    """Sync all repos in parallel"""
    start = datetime.now()
    logger.info("🚀 Starting BROski Brain sync (async)...")

    connector = aiohttp.TCPConnector(limit=10)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [sync_repo(session, repo) for repo in REPOS]
        results = await asyncio.gather(*tasks)

    # Summarize
    synced = sum(1 for r in results if r.success)
    failed = sum(1 for r in results if not r.success)
    total_issues = sum(r.issue_count for r in results)
    duration = (datetime.now() - start).total_seconds() * 1000

    summary = SyncSummary(
        total_repos=len(REPOS),
        synced_repos=synced,
        failed_repos=failed,
        total_issues=total_issues,
        total_duration_ms=duration,
        results=results
    )

    # Log summary
    logger.info(f"📊 Summary: {synced}/{len(REPOS)} repos synced, {total_issues} total issues")
    logger.info(f"⏱️  Total time: {duration:.0f}ms")
    if failed > 0:
        logger.warning(f"⚠️  {failed} repo(s) failed")

    return summary


# ========== MAIN ==========

async def main():
    """Entry point"""
    validate_config()
    try:
        summary = await sync_all_repos()
        logger.info("✅ GitHub → Obsidian DONE BROski⚡♾️")
        return 0
    except Exception as e:
        logger.error(f"❌ Sync failed: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
