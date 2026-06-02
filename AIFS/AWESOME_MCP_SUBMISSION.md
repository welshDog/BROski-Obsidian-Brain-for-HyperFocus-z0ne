# AIFS — awesome-mcp-servers Submission

> **Copy this into a PR on [punkpeye/awesome-mcp-servers](https://github.com/punkpeye/awesome-mcp-servers)**
> or [wong2/awesome-mcp-servers](https://github.com/wong2/awesome-mcp-servers)

---

## PR Title

```
Add AIFS — AI File System MCP Server (folder contract protocol + enforcement)
```

## PR Body

```markdown
## What is AIFS?

AIFS (AI File System) is a **folder contract protocol** for AI agents.
It exposes folder-level governance rules as MCP resources, so AI tools
(Claude, Cursor, Windsurf) can read and respect per-folder permissions natively.

## What does the MCP server expose?

### Resources
- `aifs://contract/{folder}` — full contract for a folder (permissions, agents, locked files)
- `aifs://agents/{folder}` — agent trust tiers (FULL / EDIT_ONLY / READ_ONLY / BLOCKED)
- `aifs://locked/{folder}` — files AI must never touch (.ailock patterns)
- `aifs://context/{folder}` — current sprint state and in-flight files
- `aifs://trust/{folder}` — per-agent trust configuration
- `aifs://overview` — full project contract tree

### Tools
- `check_permission` — check if action is allowed before doing it
- `get_contract` — get full contract for a folder
- `get_trust_level` — get trust level for a specific agent
- `list_locked_files` — list hard-locked files
- `get_project_overview` — full project governance summary

### Prompts
- `aifs_rules` — system prompt injection with all active rules
- `aifs_context` — current sprint context for the active folder

## Install

```bash
git clone https://github.com/welshDog/BROski-Obsidian-Brain-for-HyperFocus-z0ne
pip install mcp cryptography fastapi uvicorn
```

Add to your MCP config:
```json
{
  "mcpServers": {
    "aifs": {
      "command": "python",
      "args": ["/path/to/AIFS/aifs_mcp_server.py", "--root", "/path/to/project"]
    }
  }
}
```

## Links

- Repo: https://github.com/welshDog/BROski-Obsidian-Brain-for-HyperFocus-z0ne
- Docs: https://github.com/welshDog/BROski-Obsidian-Brain-for-HyperFocus-z0ne/blob/main/AIFS.md
- MCP server: `AIFS/aifs_mcp_server.py`
- License: MIT
```

---

## Entry to Add (in the README table)

Find the **Developer Tools** or **File System** section and add:

```markdown
| [AIFS](https://github.com/welshDog/BROski-Obsidian-Brain-for-HyperFocus-z0ne) | Folder contract protocol for AI agents — per-folder permissions, enforcement daemon, Ed25519 signing, live dashboard, public registry | Python | MIT |
```

---

## Other Registries to Submit To

| Registry | URL | Notes |
|----------|-----|-------|
| punkpeye/awesome-mcp-servers | https://github.com/punkpeye/awesome-mcp-servers | Most popular — do this first |
| wong2/awesome-mcp-servers | https://github.com/wong2/awesome-mcp-servers | Second largest |
| mcp.so | https://mcp.so | Web registry — submit via form |
| Smithery | https://smithery.ai | MCP marketplace |
| glama.ai/mcp | https://glama.ai/mcp/servers | AI tools directory |
| dev.to | https://dev.to | Post the blog post |
| Hacker News | https://news.ycombinator.com/submit | "Show HN: AIFS — folder contracts for AI agents" |
