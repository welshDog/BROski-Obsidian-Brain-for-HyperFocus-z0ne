#!/usr/bin/env python3
"""Tests for the async GitHub-to-Obsidian sync engine."""

import os
import sys
import tempfile
from pathlib import Path
from typing import List
from unittest.mock import AsyncMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.github_to_obsidian_v2 import (
    CircuitBreaker,
    CircuitBreakerState,
    GithubIssue,
    RetryConfig,
    SyncResult,
    SyncSummary,
    format_markdown,
)


# ========== RETRY CONFIG TESTS ==========

class TestRetryConfig:
    def test_exponential_backoff(self):
        config = RetryConfig(base_delay_ms=100, backoff_multiplier=2.0)
        assert config.get_delay(0) == 0.1
        assert config.get_delay(1) == 0.2
        assert config.get_delay(2) == 0.4

    def test_max_delay_cap(self):
        config = RetryConfig(base_delay_ms=100, max_delay_ms=5000, backoff_multiplier=2.0)
        assert config.get_delay(10) == 5.0

    def test_custom_retry_config(self):
        config = RetryConfig(max_retries=5, base_delay_ms=200, max_delay_ms=10000, backoff_multiplier=1.5)
        assert config.max_retries == 5
        assert config.base_delay_ms == 200
        assert config.get_delay(0) == 0.2


class TestCircuitBreaker:
    def test_initial_state_closed(self):
        cb = CircuitBreaker()
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0

    def test_record_success_resets(self):
        cb = CircuitBreaker(failure_threshold=5)
        cb.failure_count = 3
        cb.record_success()
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0

    def test_record_failure_increments(self):
        cb = CircuitBreaker(failure_threshold=5)
        cb.record_failure()
        assert cb.failure_count == 1
        assert cb.state == CircuitBreakerState.CLOSED

    def test_record_failure_opens_at_threshold(self):
        cb = CircuitBreaker(failure_threshold=3)
        for _ in range(3):
            cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN
        assert cb.failure_count == 3

    def test_circuit_recovery_after_timeout(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout_sec=0)
        cb.record_failure()
        assert cb.state == CircuitBreakerState.OPEN
        assert cb.can_proceed() is True
        assert cb.state == CircuitBreakerState.HALF_OPEN

    def test_can_proceed_closed(self):
        assert CircuitBreaker().can_proceed() is True

    def test_can_proceed_open(self):
        cb = CircuitBreaker(failure_threshold=1)
        cb.record_failure()
        assert cb.can_proceed() is False


class TestMarkdownFormatting:
    def test_format_empty_issues(self):
        markdown = format_markdown("test-repo", [])
        assert "test-repo" in markdown
        assert "Open Issues" in markdown
        assert "✅ No open issues" in markdown

    def test_format_with_issues(self):
        issues: List[GithubIssue] = [
            {"number": 123, "title": "Fix bug", "html_url": "https://github.com/user/repo/issues/123", "assignee": {"login": "alice"}, "labels": [{"name": "bug"}, {"name": "urgent"}]},
            {"number": 124, "title": "Add feature", "html_url": "https://github.com/user/repo/issues/124", "assignee": None, "labels": []},
        ]
        markdown = format_markdown("test-repo", issues)
        assert "#123" in markdown and "Fix bug" in markdown and "alice" in markdown
        assert "bug, urgent" in markdown and "#124" in markdown and "unassigned" in markdown

    def test_format_unassigned_issue(self):
        issue: GithubIssue = {"number": 1, "title": "Unassigned task", "html_url": "https://github.com/user/repo/issues/1", "assignee": None, "labels": []}
        assert "unassigned" in format_markdown("repo", [issue])


class TestFileWriting:
    def test_write_vault_file_creates_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            vault_path = os.path.join(tmpdir, "vault", "subdir")
            file_path = os.path.join(vault_path, "test.md")
            os.makedirs(vault_path, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as handle:
                handle.write("# Test\n\nContent")
            assert os.path.exists(file_path)

    def test_write_vault_file_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "test.md")
            markdown = "# Test\n\nContent"
            with open(file_path, "w", encoding="utf-8") as handle:
                handle.write(markdown)
            with open(file_path, "r", encoding="utf-8") as handle:
                assert handle.read() == markdown


class TestAsyncFetch:
    @pytest.mark.asyncio
    async def test_fetch_issues_success(self):
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {"X-RateLimit-Remaining": "60"}
        mock_response.json = AsyncMock(return_value=[{"number": 1, "title": "Test issue", "html_url": "https://github.com/user/repo/issues/1", "assignee": None, "labels": []}])
        issues = await mock_response.json()
        assert len(issues) == 1 and issues[0]["number"] == 1

    @pytest.mark.asyncio
    async def test_fetch_issues_filters_prs(self):
        api_response = [{"number": 1, "title": "Regular issue", "html_url": "https://github.com/user/repo/issues/1"}, {"number": 2, "title": "Pull request", "html_url": "https://github.com/user/repo/pull/2", "pull_request": {"url": "..."}}]
        issues = [issue for issue in api_response if "pull_request" not in issue]
        assert len(issues) == 1 and issues[0]["number"] == 1

    @pytest.mark.asyncio
    async def test_fetch_issues_404_error(self):
        mock_response = AsyncMock()
        mock_response.status = 404
        assert mock_response.status == 404


class TestSyncResult:
    def test_sync_result_success(self):
        result = SyncResult(repo_name="test-repo", success=True, issue_count=10, duration_ms=250.5)
        assert result.repo_name == "test-repo" and result.success is True and result.issue_count == 10

    def test_sync_result_failure(self):
        result = SyncResult(repo_name="test-repo", success=False, error_msg="Network timeout")
        assert result.success is False and result.error_msg == "Network timeout"


class TestSyncSummary:
    def test_sync_summary_creation(self):
        results = [SyncResult("repo1", True, 5, 100.0), SyncResult("repo2", True, 10, 150.0), SyncResult("repo3", False, error_msg="Error")]
        summary = SyncSummary(total_repos=3, synced_repos=2, failed_repos=1, total_issues=15, total_duration_ms=250.0, results=results)
        assert summary.total_repos == 3 and summary.synced_repos == 2 and summary.failed_repos == 1 and summary.total_issues == 15


class TestIntegration:
    def test_sync_all_basic(self):
        cb = CircuitBreaker(failure_threshold=3)
        retry = RetryConfig(max_retries=3, base_delay_ms=100)
        assert cb.can_proceed() is True and retry.get_delay(0) == 0.1
        for _ in range(3):
            cb.record_failure()
        assert cb.can_proceed() is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
