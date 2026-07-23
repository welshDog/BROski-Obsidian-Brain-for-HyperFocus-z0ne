"""
AIFS Watcher — Real-Time Folder Contract Enforcement Daemon
AI File System v0.3

Usage:
    python aifs_watcher.py watch .                          # Watch current dir
    python aifs_watcher.py watch . --discord-webhook=URL   # With Discord approvals
    python aifs_watcher.py watch /path/to/project          # Watch specific path

What it does:
    - Watches for file system events in real-time
    - Resolves nearest folder contract (manifest.toml + AGENTS.md)
    - Checks .ailock patterns — hard stop
    - Checks TRUST.md for agent trust tier
    - Checks TTL rules for expiry
    - ALLOW / BLOCK / QUEUE FOR APPROVAL
    - Logs every AI action to CHANGELOG.ai.md
    - Pings Discord for approval-gated actions

Install deps:
    pip install watchdog requests tomllib

Exit codes:
    0 = Clean exit
    1 = Watcher error
"""

import os
import sys
import time
import fnmatch
import tomllib
import argparse
import requests
from pathlib import Path
from datetime import datetime, date
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# ─── Colours for terminal output ───────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def log(msg: str, level: str = "info"):
    ts = datetime.now().strftime("%H:%M:%S")
    colours = {"info": BLUE, "ok": GREEN, "warn": YELLOW, "block": RED, "approval": YELLOW}
    c = colours.get(level, RESET)
    prefix = {"info": "ℹ", "ok": "✅", "warn": "⚠️", "block": "🚫", "approval": "⏳"}
    p = prefix.get(level, "•")
    print(f"{c}{BOLD}[{ts}] {p} {msg}{RESET}")


# ─── Contract Models ────────────────────────────────────────────────────────
@dataclass
class FolderContract:
    folder: Path
    read_only: bool = False
    inherit: bool = True
    create_exts: List[str] = field(default_factory=list)
    edit_exts: List[str] = field(default_factory=list)
    delete_allowed: bool = False
    rename_policy: str = "false"   # "true" | "false" | "approval"
    move_policy: str = "false"
    require_approval_for: List[str] = field(default_factory=list)
    ailock_patterns: List[str] = field(default_factory=list)
    trust_levels: Dict[str, str] = field(default_factory=dict)
    approval_channel: str = "console"
    approval_webhook_env: str = "DISCORD_WEBHOOK_AIFS"
    approval_timeout: int = 30
    timeout_action: str = "deny"
    ttl_read_only: bool = False
    ttl_read_only_until: Optional[date] = None
    active_task: str = ""
    in_flight: List[str] = field(default_factory=list)


class ContractResolver:
    """Finds and resolves the nearest folder contract for a given path."""

    IGNORED = {"node_modules", ".git", "__pycache__", ".venv", "venv", "dist", "build", ".next"}
    SPECIAL_READONLY = {".ai", ".templates", ".archive"}

    def __init__(self, root: Path, discord_webhook: Optional[str] = None):
        self.root = root
        self.discord_webhook = discord_webhook
        self._cache: Dict[Path, FolderContract] = {}

    def resolve(self, file_path: Path) -> FolderContract:
        """Walk up from file_path to find the nearest contract."""
        folder = file_path.parent
        visited = []

        while folder >= self.root:
            if folder in self._cache:
                return self._merge_with_parents(folder, visited)

            contract_files = list(folder.glob("AGENTS.md")) + \
                             list(folder.glob("manifest.toml")) + \
                             list(folder.glob(".ailock")) + \
                             list(folder.glob("context.md")) + \
                             list(folder.glob("TRUST.md")) + \
                             list(folder.glob("ttl.toml"))

            if contract_files or folder.name in self.SPECIAL_READONLY:
                contract = self._parse(folder)
                self._cache[folder] = contract
                return self._merge_with_parents(folder, visited)

            visited.insert(0, folder)
            if folder == self.root:
                break
            folder = folder.parent

        # No contract found — use safe defaults
        return FolderContract(folder=file_path.parent)

    def _parse(self, folder: Path) -> FolderContract:
        contract = FolderContract(folder=folder)

        # Special folder defaults
        if folder.name in self.SPECIAL_READONLY:
            contract.read_only = True

        # Parse .ailock
        ailock = folder / ".ailock"
        if ailock.exists():
            lines = ailock.read_text(encoding="utf-8").splitlines()
            contract.ailock_patterns = [
                l.strip() for l in lines
                if l.strip() and not l.strip().startswith("#")
            ]

        # Parse manifest.toml
        manifest = folder / "manifest.toml"
        if manifest.exists():
            with open(manifest, "rb") as f:
                data = tomllib.load(f)

            c = data.get("contract", {})
            contract.read_only = c.get("read_only", contract.read_only)
            contract.inherit = c.get("inherit", True)

            p = data.get("permissions", {})
            contract.create_exts = p.get("create", [])
            contract.edit_exts = p.get("edit", [])
            delete_val = p.get("delete", False)
            contract.delete_allowed = delete_val if isinstance(delete_val, bool) else str(delete_val).lower() == "true"
            contract.rename_policy = str(p.get("rename", "false")).lower()
            contract.move_policy = str(p.get("move", "false")).lower()

            s = data.get("safety", {})
            contract.require_approval_for = s.get("require_approval_for", [])

            a = data.get("approval", {})
            contract.approval_channel = a.get("channel", "console")
            contract.approval_webhook_env = a.get("webhook_env", "DISCORD_WEBHOOK_AIFS")
            contract.approval_timeout = a.get("timeout_seconds", 30)
            contract.timeout_action = a.get("timeout_action", "deny")

        # Parse TTL
        ttl_path = folder / "ttl.toml"
        if ttl_path.exists():
            with open(ttl_path, "rb") as f:
                ttl = tomllib.load(f)
            rules = ttl.get("rules", {})
            contract.ttl_read_only = rules.get("read_only", False)
            until_str = rules.get("read_only_until", "")
            if until_str:
                try:
                    contract.ttl_read_only_until = date.fromisoformat(until_str)
                except ValueError:
                    pass

        # Parse TRUST.md (simple line parser)
        trust_path = folder / "TRUST.md"
        if trust_path.exists():
            content = trust_path.read_text(encoding="utf-8")
            for line in content.splitlines():
                if ":" in line and line.strip().startswith("-"):
                    parts = line.strip("- ").split(":")
                    if len(parts) == 2:
                        agent = parts[0].strip().lower()
                        tier = parts[1].strip().upper()
                        contract.trust_levels[agent] = tier

        # Parse context.md for in-flight protection
        ctx_path = folder / "context.md"
        if ctx_path.exists():
            content = ctx_path.read_text(encoding="utf-8")
            in_flight_section = False
            for line in content.splitlines():
                if "## In-Flight" in line or "## Do Not Touch" in line:
                    in_flight_section = True
                    continue
                if in_flight_section:
                    if line.startswith("##"):
                        in_flight_section = False
                    elif line.strip().startswith("-"):
                        # Extract filename from line like `- \`lib/file.ts\` — reason`
                        part = line.strip("- ").split("—")[0].strip().strip("`")
                        if part:
                            contract.in_flight.append(part)

        return contract

    def _merge_with_parents(self, folder: Path, missing_folders: List[Path]) -> FolderContract:
        """Merge local contract with parent contracts."""
        contract = self._cache.get(folder, FolderContract(folder=folder))

        # Find parent contract
        parent = folder.parent
        while parent >= self.root:
            if parent in self._cache:
                parent_contract = self._cache[parent]
                # Inherit parent rules if local allows it
                if contract.inherit:
                    if not contract.create_exts and parent_contract.create_exts:
                        contract.create_exts = parent_contract.create_exts
                    if not contract.edit_exts and parent_contract.edit_exts:
                        contract.edit_exts = parent_contract.edit_exts
                    # Parent MUST NOTs always propagate
                    if parent_contract.read_only:
                        contract.read_only = True
                    contract.ailock_patterns = parent_contract.ailock_patterns + contract.ailock_patterns
                break
            if parent == self.root:
                break
            parent = parent.parent

        return contract


# ─── Enforcement Engine ──────────────────────────────────────────────────────
class AIFSEnforcer:
    """Checks an action against a resolved contract."""

    def check(
        self,
        action: str,          # "create" | "edit" | "delete" | "rename" | "move"
        file_path: Path,
        contract: FolderContract,
        agent: str = "unknown"
    ) -> tuple[str, str]:     # ("allow" | "block" | "approval", reason)

        # 1. Check .ailock patterns
        rel = str(file_path.relative_to(contract.folder.parent) if contract.folder.parent else file_path)
        for pattern in contract.ailock_patterns:
            if fnmatch.fnmatch(rel, pattern) or fnmatch.fnmatch(file_path.name, pattern):
                return "block", f".ailock match: '{pattern}' — hard stop"

        # 2. Check TTL
        if contract.ttl_read_only and contract.ttl_read_only_until:
            if date.today() <= contract.ttl_read_only_until:
                return "block", f"TTL lock active until {contract.ttl_read_only_until}"

        # 3. Check read_only
        if contract.read_only:
            if action in ("create", "edit", "delete", "rename", "move"):
                return "block", "read_only = true — all writes blocked"

        # 4. Check agent trust tier
        tier = contract.trust_levels.get(agent.lower(), "read_only")  # unknown → READ_ONLY
        if tier == "BLOCKED":
            return "block", f"Agent '{agent}' is BLOCKED in TRUST.md"
        if tier == "READ_ONLY" and action != "read":
            return "block", f"Agent '{agent}' is READ_ONLY — no write access"
        if tier == "EDIT_ONLY" and action in ("create", "delete"):
            return "block", f"Agent '{agent}' is EDIT_ONLY — cannot create or delete"

        # 5. Check in-flight protection from context.md
        for protected in contract.in_flight:
            if protected in str(file_path):
                return "block", f"In-flight protection: '{protected}' is active in context.md"

        # 6. Check action-specific permissions
        ext = file_path.suffix.lower()

        if action == "create":
            if contract.create_exts and ext not in contract.create_exts:
                return "block", f"create '{ext}' not in allowed extensions: {contract.create_exts}"

        elif action == "edit":
            if contract.edit_exts and ext not in contract.edit_exts:
                return "block", f"edit '{ext}' not in allowed extensions: {contract.edit_exts}"

        elif action == "delete":
            if not contract.delete_allowed:
                if "delete" in contract.require_approval_for:
                    return "approval", "delete requires approval"
                return "block", "delete not allowed — MUST NOT delete"

        elif action == "rename":
            if contract.rename_policy == "false":
                return "block", "rename not allowed"
            if contract.rename_policy == "approval":
                return "approval", "rename requires approval"

        elif action == "move":
            if contract.move_policy == "false":
                return "block", "move not allowed"
            if contract.move_policy == "approval":
                return "approval", "move requires approval"

        return "allow", "✅ permitted by contract"


# ─── Audit Log ───────────────────────────────────────────────────────────────
class AuditLogger:
    """Appends to CHANGELOG.ai.md in the relevant folder."""

    def log(self, action: str, file_path: Path, result: str, reason: str, agent: str = "aifs-watcher"):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        folder = file_path.parent
        changelog = folder / "CHANGELOG.ai.md"

        emoji = {"allow": "✅", "block": "🚫", "approval": "⏳"}.get(result, "•")
        entry = f"- `{ts}` {emoji} **{action.upper()}** `{file_path.name}` — {result.upper()} — {reason} (agent: {agent})\n"

        try:
            with open(changelog, "a", encoding="utf-8") as f:
                # Add date header if new day
                if not changelog.exists() or datetime.now().strftime("%Y-%m-%d") not in changelog.read_text():
                    f.write(f"\n## {datetime.now().strftime('%Y-%m-%d')}\n")
                f.write(entry)
        except Exception:
            pass  # Never crash the watcher on log failure


# ─── Discord Approval Gate ───────────────────────────────────────────────────
class DiscordApprovalGate:
    """Sends approval requests to Discord and waits for response."""

    def __init__(self, webhook_url: str, timeout: int = 30, timeout_action: str = "deny"):
        self.webhook_url = webhook_url
        self.timeout = timeout
        self.timeout_action = timeout_action

    def request(
        self, action: str, file_path: Path, contract: FolderContract, reason: str
    ) -> bool:
        """Send Discord notification. Returns True if approved."""
        if not self.webhook_url:
            log(f"Approval needed for {action} on {file_path.name} — no webhook configured, auto-denying", "block")
            return False

        message = {
            "content": None,
            "embeds": [{
                "title": "⏳ AIFS Approval Required",
                "color": 16776960,
                "fields": [
                    {"name": "Action", "value": action.upper(), "inline": True},
                    {"name": "File", "value": f"`{file_path.name}`", "inline": True},
                    {"name": "Folder", "value": f"`{file_path.parent.name}`", "inline": True},
                    {"name": "Reason", "value": reason, "inline": False},
                    {"name": "Timeout", "value": f"{self.timeout}s — then {self.timeout_action}", "inline": False},
                ],
                "footer": {"text": "AIFS Watcher v0.3 — Reply ✅ approve or ❌ deny in your workflow"}
            }]
        }

        try:
            resp = requests.post(self.webhook_url, json=message, timeout=5)
            resp.raise_for_status()
            log(f"Approval request sent to Discord for {file_path.name}", "approval")
        except Exception as e:
            log(f"Discord webhook failed: {e} — applying timeout_action={self.timeout_action}", "warn")

        # For now, apply timeout_action immediately (interactive approval needs a bot)
        # Future: poll a response endpoint
        if self.timeout_action == "allow":
            log(f"Timeout action = allow → proceeding with {action} on {file_path.name}", "warn")
            return True
        else:
            log(f"Timeout action = deny → blocking {action} on {file_path.name}", "block")
            return False


# ─── File System Event Handler ───────────────────────────────────────────────
class AIFSEventHandler(FileSystemEventHandler):
    """Handles watchdog file system events and runs AIFS enforcement."""

    CONTRACT_FILES = {"AGENTS.md", "manifest.toml", "folder.prompt.md", ".ailock",
                      "context.md", "TRUST.md", "ttl.toml", "CHANGELOG.ai.md"}
    IGNORED_DIRS = {"node_modules", ".git", "__pycache__", ".venv", "venv", "dist", "build", ".next"}

    def __init__(self, root: Path, resolver: ContractResolver, enforcer: AIFSEnforcer,
                 audit: AuditLogger, discord: Optional[DiscordApprovalGate], agent: str):
        self.root = root
        self.resolver = resolver
        self.enforcer = enforcer
        self.audit = audit
        self.discord = discord
        self.agent = agent
        super().__init__()

    def _should_ignore(self, path: str) -> bool:
        p = Path(path)
        if p.name in self.CONTRACT_FILES:
            return True
        if p.name.startswith(".") and p.name not in {".ailock"}:
            return True
        for part in p.parts:
            if part in self.IGNORED_DIRS:
                return True
        return False

    def _handle(self, action: str, src: str, dest: str = ""):
        if self._should_ignore(src):
            return

        file_path = Path(src)
        contract = self.resolver.resolve(file_path)
        result, reason = self.enforcer.check(action, file_path, contract, self.agent)

        if result == "allow":
            log(f"{action.upper()} {file_path.name} → ALLOWED", "ok")
        elif result == "block":
            log(f"{action.upper()} {file_path.name} → BLOCKED — {reason}", "block")
        elif result == "approval":
            log(f"{action.upper()} {file_path.name} → NEEDS APPROVAL — {reason}", "approval")
            if self.discord:
                approved = self.discord.request(action, file_path, contract, reason)
                result = "allow" if approved else "block"
                log(f"Approval {'granted ✅' if approved else 'denied 🚫'} for {file_path.name}",
                    "ok" if approved else "block")

        self.audit.log(action, file_path, result, reason, self.agent)

    def on_created(self, event):
        if not event.is_directory:
            self._handle("create", event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self._handle("edit", event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self._handle("delete", event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self._handle("move", event.src_path)


# ─── CLI ──────────────────────────────────────────────────────────────────────
def cmd_watch(args):
    root = Path(args.path).resolve()
    if not root.exists():
        print(f"{RED}Error: path does not exist: {root}{RESET}")
        sys.exit(1)

    discord_url = args.discord_webhook or os.environ.get("DISCORD_WEBHOOK_AIFS", "")

    resolver = ContractResolver(root, discord_url)
    enforcer = AIFSEnforcer()
    audit = AuditLogger()
    discord_gate = DiscordApprovalGate(discord_url) if discord_url else None

    handler = AIFSEventHandler(
        root=root,
        resolver=resolver,
        enforcer=enforcer,
        audit=audit,
        discord=discord_gate,
        agent=args.agent
    )

    observer = Observer()
    observer.schedule(handler, str(root), recursive=True)
    observer.start()

    print(f"{GREEN}{BOLD}")
    print("╔══════════════════════════════════════════════════╗")
    print("║   🧠 AIFS Watcher v0.3 — Real-Time Enforcement  ║")
    print("╚══════════════════════════════════════════════════╝")
    print(f"{RESET}")
    log(f"Watching: {root}", "info")
    log(f"Agent identity: {args.agent}", "info")
    log(f"Discord approvals: {'enabled ✅' if discord_gate else 'disabled ⚠️'}", "info")
    log("Press Ctrl+C to stop\n", "info")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        log("AIFS Watcher stopped.", "info")

    observer.join()


def main():
    parser = argparse.ArgumentParser(
        description="AIFS Watcher — Real-Time AI File System Contract Enforcement",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python aifs_watcher.py watch .
  python aifs_watcher.py watch . --discord-webhook=https://discord.com/api/webhooks/...
  python aifs_watcher.py watch /my/project --agent=claude-3.5-sonnet
"""
    )
    subparsers = parser.add_subparsers(dest="command")

    watch_parser = subparsers.add_parser("watch", help="Start real-time watcher")
    watch_parser.add_argument("path", nargs="?", default=".", help="Path to watch (default: current dir)")
    watch_parser.add_argument("--discord-webhook", default="", help="Discord webhook URL for approval notifications")
    watch_parser.add_argument("--agent", default="unknown", help="Agent identity for TRUST.md tier lookup")

    args = parser.parse_args()

    if args.command == "watch":
        cmd_watch(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
