"""
AIFS MCP Server v0.4
AI File System — MCP Resource Integration

Exposes AIFS folder contracts as MCP resources so any AI tool
(Claude Desktop, Cursor, Windsurf, Cline, etc.) can discover
and read contracts natively — zero config needed.

Resources exposed:
    aifs://contracts/list              — all contracts found in watched root
    aifs://folder/{path}               — resolved contract for a specific folder
    aifs://ailock/{path}               — .ailock patterns for a folder
    aifs://context/{path}              — context.md for a folder
    aifs://trust/{path}                — TRUST.md tiers for a folder
    aifs://changelog/{path}            — CHANGELOG.ai.md for a folder

Tools exposed:
    check_action(action, file_path, agent)  — ask if an action is allowed
    resolve_contract(folder_path)           — get full resolved contract
    list_locked_paths(root)                 — all .ailock-protected paths
    get_context(folder_path)                — get live sprint state
    get_in_flight(folder_path)              — get in-flight files (do not touch)

Prompts exposed:
    folder_briefing(folder_path)            — AI briefing for a folder
    sprint_checklist(folder_path)           — pre-edit safety checklist

Install deps:
    pip install mcp watchdog requests tomllib

Run:
    python AIFS/aifs_mcp_server.py
    python AIFS/aifs_mcp_server.py --root /path/to/project
    python AIFS/aifs_mcp_server.py --root . --transport stdio

For Claude Desktop, add to claude_desktop_config.json:
    {
      "mcpServers": {
        "aifs": {
          "command": "python",
          "args": ["/path/to/AIFS/aifs_mcp_server.py", "--root", "/path/to/project"]
        }
      }
    }
"""

import os
import sys
import json
import fnmatch
import argparse
import tomllib
from pathlib import Path
from datetime import datetime, date
from typing import Optional, Any

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp import types
except ImportError:
    print("ERROR: mcp package not installed. Run: pip install mcp", file=sys.stderr)
    sys.exit(1)

# Import contract resolution from aifs_watcher
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))
try:
    from aifs_watcher import ContractResolver, AIFSEnforcer, FolderContract
except ImportError:
    print("ERROR: aifs_watcher.py must be in the same directory.", file=sys.stderr)
    sys.exit(1)


# ─── AIFS MCP Server ──────────────────────────────────────────────────────────
server = Server("aifs")
ROOT: Path = Path(".").resolve()
resolver: Optional[ContractResolver] = None
enforcer: Optional[AIFSEnforcer] = None


def get_resolver() -> ContractResolver:
    global resolver
    if resolver is None:
        resolver = ContractResolver(ROOT)
    return resolver


def get_enforcer() -> AIFSEnforcer:
    global enforcer
    if enforcer is None:
        enforcer = AIFSEnforcer()
    return enforcer


def contract_to_dict(c: FolderContract) -> dict:
    return {
        "folder": str(c.folder),
        "read_only": c.read_only,
        "inherit": c.inherit,
        "create_exts": c.create_exts,
        "edit_exts": c.edit_exts,
        "delete_allowed": c.delete_allowed,
        "rename_policy": c.rename_policy,
        "move_policy": c.move_policy,
        "require_approval_for": c.require_approval_for,
        "ailock_patterns": c.ailock_patterns,
        "trust_levels": c.trust_levels,
        "approval_channel": c.approval_channel,
        "ttl_read_only": c.ttl_read_only,
        "ttl_read_only_until": str(c.ttl_read_only_until) if c.ttl_read_only_until else None,
        "in_flight": c.in_flight,
        "active_task": c.active_task,
    }


def find_all_contracts(root: Path) -> list[dict]:
    """Walk the tree and find all folders with AIFS contracts."""
    IGNORED = {"node_modules", ".git", "__pycache__", ".venv", "venv", "dist", "build", ".next"}
    CONTRACT_FILES = {"AGENTS.md", "manifest.toml", "folder.prompt.md", ".ailock", "context.md", "TRUST.md"}
    results = []

    for folder in root.rglob("*"):
        if not folder.is_dir():
            continue
        if any(p in IGNORED for p in folder.parts):
            continue
        found_files = [f.name for f in folder.iterdir() if f.name in CONTRACT_FILES]
        if found_files:
            rel = str(folder.relative_to(root))
            results.append({
                "folder": rel,
                "contract_files": found_files,
                "uri": f"aifs://folder/{rel}"
            })

    return results


def read_context(folder: Path) -> dict:
    ctx_path = folder / "context.md"
    if not ctx_path.exists():
        return {"exists": False, "active_task": "", "in_flight": [], "approved": [], "raw": ""}

    content = ctx_path.read_text(encoding="utf-8")
    in_flight = []
    approved = []
    active_task = ""
    section = None

    for line in content.splitlines():
        if "## Active Task" in line:
            section = "task"
        elif "## In-Flight" in line or "## Do Not Touch" in line:
            section = "inflight"
        elif "## Approved" in line:
            section = "approved"
        elif line.startswith("##"):
            section = None
        elif section == "task" and line.strip() and not line.startswith("#"):
            active_task = line.strip()
        elif section == "inflight" and line.strip().startswith("-"):
            part = line.strip("- ").split("—")[0].strip().strip("`")
            if part:
                in_flight.append(part)
        elif section == "approved" and line.strip().startswith("-"):
            part = line.strip("- ").strip().strip("`")
            if part:
                approved.append(part)

    return {
        "exists": True,
        "active_task": active_task,
        "in_flight": in_flight,
        "approved": approved,
        "raw": content
    }


# ─── Resources ────────────────────────────────────────────────────────────────────
@server.list_resources()
async def list_resources() -> list[types.Resource]:
    resources = [
        types.Resource(
            uri="aifs://contracts/list",
            name="All AIFS Contracts",
            description="List of all folders with AIFS contracts in the watched root.",
            mimeType="application/json"
        )
    ]

    # Dynamically add a resource per discovered contract folder
    contracts = find_all_contracts(ROOT)
    for c in contracts:
        folder = c["folder"]
        resources.append(types.Resource(
            uri=f"aifs://folder/{folder}",
            name=f"Contract: {folder}",
            description=f"Resolved AIFS contract for /{folder} ({', '.join(c['contract_files'])})",
            mimeType="application/json"
        ))
        resources.append(types.Resource(
            uri=f"aifs://context/{folder}",
            name=f"Context: {folder}",
            description=f"Live sprint state for /{folder}",
            mimeType="application/json"
        ))

    return resources


@server.read_resource()
async def read_resource(uri: types.AnyUrl) -> str:
    uri_str = str(uri)

    # All contracts list
    if uri_str == "aifs://contracts/list":
        contracts = find_all_contracts(ROOT)
        return json.dumps({
            "root": str(ROOT),
            "total": len(contracts),
            "contracts": contracts
        }, indent=2)

    # Resolved contract for a folder
    if uri_str.startswith("aifs://folder/"):
        rel = uri_str.removeprefix("aifs://folder/")
        folder = ROOT / rel
        if not folder.exists():
            return json.dumps({"error": f"Folder not found: {rel}"})
        file_path = folder / "_dummy_check.md"  # dummy to resolve contract
        contract = get_resolver().resolve(file_path)
        return json.dumps(contract_to_dict(contract), indent=2)

    # .ailock patterns
    if uri_str.startswith("aifs://ailock/"):
        rel = uri_str.removeprefix("aifs://ailock/")
        folder = ROOT / rel
        ailock = folder / ".ailock"
        if not ailock.exists():
            return json.dumps({"exists": False, "patterns": []})
        lines = ailock.read_text(encoding="utf-8").splitlines()
        patterns = [l.strip() for l in lines if l.strip() and not l.strip().startswith("#")]
        return json.dumps({"exists": True, "folder": rel, "patterns": patterns}, indent=2)

    # context.md
    if uri_str.startswith("aifs://context/"):
        rel = uri_str.removeprefix("aifs://context/")
        folder = ROOT / rel
        ctx = read_context(folder)
        ctx["folder"] = rel
        return json.dumps(ctx, indent=2)

    # TRUST.md
    if uri_str.startswith("aifs://trust/"):
        rel = uri_str.removeprefix("aifs://trust/")
        folder = ROOT / rel
        trust_path = folder / "TRUST.md"
        if not trust_path.exists():
            return json.dumps({"exists": False, "trust_levels": {}, "default": "READ_ONLY"})
        content = trust_path.read_text(encoding="utf-8")
        tiers = {}
        for line in content.splitlines():
            if ":" in line and line.strip().startswith("-"):
                parts = line.strip("- ").split(":")
                if len(parts) == 2:
                    tiers[parts[0].strip().lower()] = parts[1].strip().upper()
        return json.dumps({"exists": True, "folder": rel, "trust_levels": tiers, "default": "READ_ONLY"}, indent=2)

    # CHANGELOG.ai.md
    if uri_str.startswith("aifs://changelog/"):
        rel = uri_str.removeprefix("aifs://changelog/")
        folder = ROOT / rel
        changelog = folder / "CHANGELOG.ai.md"
        if not changelog.exists():
            return json.dumps({"exists": False, "entries": []})
        return changelog.read_text(encoding="utf-8")

    return json.dumps({"error": f"Unknown resource URI: {uri_str}"})


# ─── Tools ─────────────────────────────────────────────────────────────────────────
@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="check_action",
            description="Ask AIFS if a specific action is permitted for a file. Returns allow/block/approval with reason.",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["create", "edit", "delete", "rename", "move"], "description": "Action to check"},
                    "file_path": {"type": "string", "description": "Relative path to the file from root"},
                    "agent": {"type": "string", "description": "Agent identity for TRUST.md lookup", "default": "unknown"}
                },
                "required": ["action", "file_path"]
            }
        ),
        types.Tool(
            name="resolve_contract",
            description="Get the fully resolved AIFS contract for a folder, including inherited rules.",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder_path": {"type": "string", "description": "Relative folder path from root"}
                },
                "required": ["folder_path"]
            }
        ),
        types.Tool(
            name="list_locked_paths",
            description="List all paths protected by .ailock across the entire project. These are hard stops.",
            inputSchema={
                "type": "object",
                "properties": {
                    "root": {"type": "string", "description": "Root path to scan (defaults to server root)", "default": "."}
                }
            }
        ),
        types.Tool(
            name="get_context",
            description="Get the live sprint context for a folder. Shows active task, in-flight files (do not touch), and approved files.",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder_path": {"type": "string", "description": "Relative folder path from root"}
                },
                "required": ["folder_path"]
            }
        ),
        types.Tool(
            name="get_in_flight",
            description="Get the list of in-flight files for a folder. These files must NOT be touched until cleared from context.md.",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder_path": {"type": "string", "description": "Relative folder path from root"}
                },
                "required": ["folder_path"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:

    if name == "check_action":
        action = arguments["action"]
        file_path = ROOT / arguments["file_path"]
        agent = arguments.get("agent", "unknown")

        contract = get_resolver().resolve(file_path)
        result, reason = get_enforcer().check(action, file_path, contract, agent)

        emoji = {"allow": "\u2705", "block": "\U0001f6ab", "approval": "\u23f3"}.get(result, "\u2022")
        response = {
            "result": result,
            "reason": reason,
            "file": arguments["file_path"],
            "action": action,
            "agent": agent,
            "folder": str(contract.folder.relative_to(ROOT)),
            "summary": f"{emoji} {result.upper()}: {action} on {Path(arguments['file_path']).name} \u2014 {reason}"
        }
        return [types.TextContent(type="text", text=json.dumps(response, indent=2))]

    elif name == "resolve_contract":
        folder_path = ROOT / arguments["folder_path"]
        dummy = folder_path / "_check.md"
        contract = get_resolver().resolve(dummy)
        return [types.TextContent(type="text", text=json.dumps(contract_to_dict(contract), indent=2))]

    elif name == "list_locked_paths":
        locked = []
        IGNORED = {"node_modules", ".git", "__pycache__", ".venv", "venv", "dist", "build"}
        for ailock_file in ROOT.rglob(".ailock"):
            if any(p in IGNORED for p in ailock_file.parts):
                continue
            folder = ailock_file.parent
            lines = ailock_file.read_text(encoding="utf-8").splitlines()
            patterns = [l.strip() for l in lines if l.strip() and not l.strip().startswith("#")]
            for p in patterns:
                locked.append({
                    "folder": str(folder.relative_to(ROOT)),
                    "pattern": p,
                    "full_pattern": str(folder.relative_to(ROOT)) + "/" + p
                })
        return [types.TextContent(type="text", text=json.dumps({
            "total_locked_patterns": len(locked),
            "locked_paths": locked
        }, indent=2))]

    elif name == "get_context":
        folder = ROOT / arguments["folder_path"]
        ctx = read_context(folder)
        ctx["folder"] = arguments["folder_path"]
        return [types.TextContent(type="text", text=json.dumps(ctx, indent=2))]

    elif name == "get_in_flight":
        folder = ROOT / arguments["folder_path"]
        ctx = read_context(folder)
        response = {
            "folder": arguments["folder_path"],
            "in_flight": ctx["in_flight"],
            "active_task": ctx["active_task"],
            "warning": "\u26a0\ufe0f Do NOT edit these files until they are removed from context.md" if ctx["in_flight"] else "\u2705 No in-flight files. Safe to proceed."
        }
        return [types.TextContent(type="text", text=json.dumps(response, indent=2))]

    return [types.TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))]


# ─── Prompts ──────────────────────────────────────────────────────────────────────
@server.list_prompts()
async def list_prompts() -> list[types.Prompt]:
    return [
        types.Prompt(
            name="folder_briefing",
            description="Generate a full AI briefing for a folder before starting work. Reads contract, context, in-flight files, and trust tier.",
            arguments=[
                types.PromptArgument(name="folder_path", description="Relative folder path from root", required=True),
                types.PromptArgument(name="agent", description="Agent identity", required=False)
            ]
        ),
        types.Prompt(
            name="sprint_checklist",
            description="Generate a pre-edit safety checklist for a folder based on its AIFS contract.",
            arguments=[
                types.PromptArgument(name="folder_path", description="Relative folder path from root", required=True)
            ]
        )
    ]


@server.get_prompt()
async def get_prompt(name: str, arguments: Optional[dict] = None) -> types.GetPromptResult:
    args = arguments or {}
    folder_path = args.get("folder_path", ".")
    agent = args.get("agent", "unknown")
    folder = ROOT / folder_path
    dummy = folder / "_check.md"
    contract = get_resolver().resolve(dummy)
    ctx = read_context(folder)

    if name == "folder_briefing":
        tier = contract.trust_levels.get(agent.lower(), "READ_ONLY")
        briefing = f"""# AIFS Folder Briefing: /{folder_path}

## Your Trust Tier
Agent: `{agent}` → **{tier}**

## Contract Rules
- Read-only: {contract.read_only}
- Create allowed: {contract.create_exts or 'any'}
- Edit allowed: {contract.edit_exts or 'any'}
- Delete allowed: {contract.delete_allowed}
- Rename policy: {contract.rename_policy}
- Approval required for: {', '.join(contract.require_approval_for) or 'nothing'}

## Hard Stops (.ailock)
{chr(10).join(f'- `{p}`' for p in contract.ailock_patterns) if contract.ailock_patterns else '- None defined'}

## Current Sprint
{ctx['active_task'] or 'No active task defined in context.md'}

## In-Flight Files (DO NOT TOUCH)
{chr(10).join(f'- `{f}`' for f in ctx['in_flight']) if ctx['in_flight'] else '- None — safe to proceed'}

## Approved to Edit
{chr(10).join(f'- `{f}`' for f in ctx['approved']) if ctx.get('approved') else '- Not specified — check context.md'}

## Before You Edit
1. Confirm your action is in the allowed list above
2. Check nothing you want to touch is in-flight
3. If unsure: STOP & ASK
4. After editing: update context.md Last AI Edit field
"""
        return types.GetPromptResult(
            description=f"AIFS briefing for /{folder_path}",
            messages=[types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=briefing)
            )]
        )

    elif name == "sprint_checklist":
        checklist = f"""# AIFS Pre-Edit Safety Checklist: /{folder_path}

Before making ANY changes, confirm:

- [ ] I have read the AGENTS.md for this folder
- [ ] I have checked context.md for in-flight files
- [ ] None of the files I want to edit are in the in-flight list
- [ ] My action (create/edit/delete) is permitted by the contract
- [ ] I am not touching any .ailock-protected paths
- [ ] I know my trust tier for this folder
- [ ] If approval is needed, I have requested it before proceeding
- [ ] After editing, I will update context.md with what I changed

## In-Flight Right Now
{chr(10).join(f'- `{f}` ⚠️ DO NOT TOUCH' for f in ctx['in_flight']) if ctx['in_flight'] else '- None — all clear ✅'}

## Hard-Locked Paths
{chr(10).join(f'- `{p}` 🚫 HARD STOP' for p in contract.ailock_patterns) if contract.ailock_patterns else '- None defined'}
"""
        return types.GetPromptResult(
            description=f"Pre-edit checklist for /{folder_path}",
            messages=[types.PromptMessage(
                role="user",
                content=types.TextContent(type="text", text=checklist)
            )]
        )

    return types.GetPromptResult(
        description="Unknown prompt",
        messages=[types.PromptMessage(role="user", content=types.TextContent(type="text", text=f"Unknown prompt: {name}"))]
    )


# ─── Entry Point ───────────────────────────────────────────────────────────────────
import asyncio

async def main_async(root: str):
    global ROOT, resolver, enforcer
    ROOT = Path(root).resolve()
    resolver = ContractResolver(ROOT)
    enforcer = AIFSEnforcer()

    print(f"AIFS MCP Server v0.4 starting...", file=sys.stderr)
    print(f"Root: {ROOT}", file=sys.stderr)
    print(f"Transport: stdio", file=sys.stderr)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


def main():
    parser = argparse.ArgumentParser(description="AIFS MCP Server v0.4")
    parser.add_argument("--root", default=".", help="Project root to serve contracts from")
    args = parser.parse_args()
    asyncio.run(main_async(args.root))


if __name__ == "__main__":
    main()
