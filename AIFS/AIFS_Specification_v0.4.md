# AIFS — AI File System Specification v0.4

> **The Folder Contract Protocol for AI Agents**
> Now with MCP Resource Integration — any AI tool discovers contracts natively.

Built by welshDog × Perplexity | June 2026

---

## What Changed in v0.4

- **MCP Server** (`aifs_mcp_server.py`) — exposes all contracts as MCP resources
- **`mcp.json`** — drop-in manifest for Claude Desktop, Cursor, Windsurf, Cline
- **6 MCP Resources** — contracts, context, ailock, trust, changelog discoverable by any tool
- **5 MCP Tools** — check_action, resolve_contract, list_locked_paths, get_context, get_in_flight
- **2 MCP Prompts** — folder_briefing, sprint_checklist
- Spec v0.3 is unchanged — v0.4 adds the MCP layer on top

---

## The Full Architecture

```
┌───────────────────────────────────────────────────────────┐
│                AI TOOL (Claude / Cursor / Windsurf)          │
│                                                              │
│  1. Tool starts session                                      │
│  2. Connects to aifs MCP server                             │
│  3. Calls get_in_flight(folder) → reads in-flight files     │
│  4. Calls check_action(edit, file.ts) → allow/block         │
│  5. Calls folder_briefing prompt → full safety context      │
│  6. Makes edit (if allowed)                                  │
└───────────────────────────────────────────────────────────┘
           │ MCP (stdio)
┌───────────────────────────────────────────────────────────┐
│  AIFS MCP Server (aifs_mcp_server.py)                       │
│                                                              │
│  Resources: contracts/list, folder/{p}, context/{p}         │
│  Tools: check_action, resolve_contract, get_in_flight       │
│  Prompts: folder_briefing, sprint_checklist                 │
└───────────────────────────────────────────────────────────┘
           │ reads contracts from disk
┌───────────────────────────────────────────────────────────┐
│  Your Project Folders                                        │
│                                                              │
│  /src ─ manifest.toml, AGENTS.md, context.md               │
│  /migrations ─ .ailock  (hard stop)                        │
│  /docs ─ folder.prompt.md, TRUST.md                        │
└───────────────────────────────────────────────────────────┘
```

---

## Quick Start (v0.4)

### 1. Install
```bash
pip install mcp watchdog requests
```

### 2. Run the server
```bash
python AIFS/aifs_mcp_server.py --root /path/to/your/project
```

### 3. Add to Claude Desktop
Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:
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

### 4. Use in Cursor
Point Cursor MCP settings at `AIFS/mcp.json`. Contracts auto-load as context.

### 5. Ask the AI
```
"Before you edit src/hooks/useProgress.ts, call check_action and folder_briefing first."
```

---

## MCP Resources

| URI | Returns | Use |
|-----|---------|-----|
| `aifs://contracts/list` | JSON list of all contracts | Discovery |
| `aifs://folder/{path}` | Resolved contract JSON | Policy check |
| `aifs://context/{path}` | Active task + in-flight files | Sprint safety |
| `aifs://ailock/{path}` | Hard-stop patterns | Pre-edit check |
| `aifs://trust/{path}` | Agent trust tiers | Permission check |
| `aifs://changelog/{path}` | AI audit log markdown | Audit |

## MCP Tools

| Tool | What It Does |
|------|--------------|
| `check_action` | Is this create/edit/delete allowed? Returns allow/block/approval |
| `resolve_contract` | Get full resolved contract for a folder |
| `list_locked_paths` | All .ailock paths across project |
| `get_context` | Active task + in-flight + approved files |
| `get_in_flight` | Just the do-not-touch list |

## MCP Prompts

| Prompt | What It Does |
|--------|--------------|
| `folder_briefing` | Full safety brief before starting work in a folder |
| `sprint_checklist` | Pre-edit checklist — tick all boxes before touching files |

---

## Roadmap

| Phase | Status |
|-------|---------|
| v0.1 — Core spec | ✅ Done |
| v0.2 — Validator + CI | ✅ Done |
| v0.3 — Watcher + TTL + TRUST + .ailock | ✅ Done |
| v0.4 — MCP resource integration | ✅ Done |
| v0.5 — AIFS Hub dashboard | 🔜 Next |
| v0.6 — Cryptographic contract signing | 🔜 Future |
| v1.0 — AIFS Registry (shareable contracts) | 🔜 Future |

---

*Built by welshDog × Perplexity — Llanelli, Wales 🏴󠁧󠁢󠁷󠁬󠁳󠁧 — June 2026*
