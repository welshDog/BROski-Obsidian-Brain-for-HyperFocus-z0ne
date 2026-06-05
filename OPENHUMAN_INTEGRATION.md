# OpenHuman Integration — BROski-Obsidian-Brain

**Your vault just became the central nervous system for everything.**

GitHub, Gmail, Slack, Claude Code, Cursor, your agents — **all read and write to the same memory store**. No silos. No context loss. One brain.

---

## 🧠 What This Gives You

| Before | After |
|--------|-------|
| Manual note-taking | OpenHuman auto-syncs GitHub issues, Gmail, Slack → your vault every 20 mins |
| Claude Code starts cold | Claude Code reads your vault context → knows everything |
| No connection between tools | GitHub webhook → vault; Slack mentions → vault; Gmail threads → vault |
| Context scattered | Everything in PARA structure; `mcp_bridge.py` queries the unified store |

---

## ⚡ Quick Start (5 min)

### 1. Run the installer

```bash
bash install_openhuman_memory.sh
```

This will:
- ✅ Auto-find your vault (or ask for the path)
- ✅ Create `~/.openhuman/.env` pointing to your vault
- ✅ Create symlink: `~/.openhuman/memory/` → `vault/00-Inbox/OpenHuman-Feed/`
- ✅ Create an Obsidian template for auto-synced notes

### 2. Install OpenHuman

**macOS:**
```bash
brew install openhuman
```

**Linux** (Fedora/Ubuntu/Arch/Nix):
```bash
# Fedora
dnf install openhuman

# Ubuntu/Debian
apt install openhuman

# Arch
pacman -S openhuman

# Nix
nix-shell -p openhuman
```

**Windows:**
- Download: https://github.com/tinyhumansai/openhuman/releases
- Extract and run `.exe`

### 3. Start OpenHuman and connect your integrations

```bash
openhuman
```

Then in the UI:
- Click **Settings** → **Integrations**
- Connect **GitHub** (one-click OAuth)
- Connect **Gmail** (optional)
- Connect **Slack** (optional)

### 4. Wait 20 mins and check your vault

```
BROski-Obsidian-Brain-for-HyperFocus-z0ne/
  HYPERFOCUS_ZONE/
    00-Inbox/
      OpenHuman-Feed/
        github-issue-123.md  ← Fresh from GitHub
        slack-channel-updates.md  ← Fresh from Slack
        gmail-thread.md  ← Fresh from Gmail
```

---

## 🔌 How It Works

### The Flow

```
GitHub/Gmail/Slack
    ↓ (OpenHuman polls every 20 mins)
~/.openhuman/memory/
    ↓ (symlink)
vault/00-Inbox/OpenHuman-Feed/
    ↓ (Obsidian syncs)
Your vault (live in Obsidian)
    ↓ (mcp_bridge.py queries)
Local LLM + Claude Code know everything
```

### Vault Structure

OpenHuman writes **Markdown files** into `00-Inbox/OpenHuman-Feed/` with YAML frontmatter:

```markdown
---
created: 2026-06-05 10:30
source: GitHub
repo: HyperCode-V2.4
event: pull_request
number: 42
url: https://github.com/welshdog/HyperCode-V2.4/pull/42
tags: [openhuman, github, pr]
status: open
---

# HyperCode-V2.4 #42 — Add vault sync integration

**Action**: opened  
**Author**: @you  

## Details
PR description here...
```

### MCP Bridge Integration

Your `mcp_bridge.py` now queries this unified store:

```python
# When Claude Code or an agent asks:
# "What are my open GitHub issues?"

# mcp_bridge now:
# 1. Searches 00-Inbox/OpenHuman-Feed/ for github-*.md files
# 2. Extracts status: open
# 3. Returns structured list to LLM
```

---

## 🛠️ Configuration

### `.env` file location

**Linux/macOS:**
```
~/.openhuman/.env
```

**Windows:**
```
%USERPROFILE%\.openhuman\.env
```

### What's in the `.env`

```bash
# Path where OpenHuman writes .md files
OPENHUMAN_WORKSPACE=/path/to/vault

# When agentmemory backend lands (future):
# MEMORY_BACKEND=agentmemory
# MEMORY_AGENTMEMORY_DB=/path/to/vault/brain.db
```

---

## 🎯 Workflow Examples

### Example 1: GitHub Issues Auto-Sync

1. Someone opens a PR on HyperCode-V2.4
2. OpenHuman fetches it (20-min poll)
3. Writes to `vault/00-Inbox/OpenHuman-Feed/github-pr-*.md`
4. You open Obsidian → see it in 00-Inbox
5. You read the PR description, click the link, review code
6. You drag the note to `01-Projects/HyperCode-V2.4/` when you start work

### Example 2: Claude Code Reads Your Brain

1. You open Claude Code
2. It loads the MCP bridge (via `mcp_bridge.py`)
3. You ask: "What should I prioritize?"
4. Claude queries your vault including OpenHuman-Feed notes
5. Claude returns: "You have 3 open PRs, 5 new GitHub issues, and 2 Slack mentions — here's prioritization"

### Example 3: Slack Notifications → Actionable Notes

1. @you is mentioned in #hypercode-dev
2. OpenHuman captures it as `slack-hypercode-dev-*.md`
3. Note lands in vault with frontmatter: `tags: [slack, hypercode-dev]`
4. You search in Obsidian: `tag:slack tag:hypercode-dev`
5. All Slack mentions aggregated, searchable

---

## 🚀 Advanced: Symlink Troubleshooting

### macOS/Linux: Symlink works out of the box
```bash
# Installer creates:
ln -s ~/vault/00-Inbox/OpenHuman-Feed ~/.openhuman/memory
```

### Windows (Git Bash / WSL): Needs admin or WSL
- **Option A (Recommended):** Run installer in WSL, use symlink
- **Option B:** Manually set vault path in OpenHuman UI instead
  - Open OpenHuman → Settings
  - Set: `Workspace Path: C:\path\to\vault`

### Windows (PowerShell): Use New-Item
```powershell
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.openhuman\memory" `
  -Target "$env:USERPROFILE\BROski-Obsidian-Brain-for-HyperFocus-z0ne\HYPERFOCUS_ZONE\00-Inbox\OpenHuman-Feed"
```

---

## 🔮 Roadmap: `agentmemory` Backend

OpenHuman is planning a **SQLite-backed memory store** called `agentmemory` for unified agent memory across tools.

**Status:** Beta (tracked at https://github.com/tinyhumansai/openhuman/issues/2620)

**When it ships, your installer will auto-upgrade to:**
```bash
MEMORY_BACKEND=agentmemory
MEMORY_AGENTMEMORY_DB=~/.openhuman/brain.db
```

**Re-run the installer** and it will configure this automatically.

Until then, **the symlink approach works perfectly today** — you get the same unified brain, just via `.md` files instead of a database.

---

## ⚠️ Known Limitations (Today)

| Limitation | Workaround | Timeline |
|---|---|---|
| OpenHuman writes to flat folder | Use Obsidian templates to organize | Native PARA support in v0.8 (Q3 2026) |
| No real-time sync (20-min poll) | Check vault every 20 mins; webhook for urgent | RT webhooks planned |
| No conflict resolution (write conflicts) | Keep `.openhuman/memory/` symlinked read-only for now | Merge strategy coming |

---

## 🧠 MCP Bridge Queries OpenHuman-Feed

Your updated `mcp_bridge.py` now includes:

```python
async def query_openhuman_feed(self, source: str = None) -> List[Dict]:
    """Query OpenHuman-synced notes.
    
    Args:
        source: 'github', 'slack', 'gmail', or None (all)
    
    Returns:
        List of note metadata dicts
    """
    feed_dir = os.path.join(self.vault_path, "00-Inbox", "OpenHuman-Feed")
    if not os.path.exists(feed_dir):
        return []
    
    notes = []
    for fname in os.listdir(feed_dir):
        if not fname.endswith(".md"):
            continue
        if source and source not in fname:
            continue
        fpath = os.path.join(feed_dir, fname)
        # Parse YAML frontmatter...
        notes.append({...})
    
    return notes
```

**Usage in your agent code:**
```python
# Get all unread GitHub issues
issues = await mcp_bridge.query_openhuman_feed(source="github")

# Filter by status
open_issues = [i for i in issues if i.get("status") == "open"]

# Query LLM: "Prioritize these issues"
result = await mcp_bridge.query_vault(
    "Given these GitHub issues, what should I prioritize?",
    context_files=[i["file"] for i in open_issues]
)
```

---

## 📝 Testing Your Setup

### Test 1: Check if symlink works

```bash
# Should show vault path
ls -la ~/.openhuman/memory

# Should not be empty after OpenHuman syncs
ls ~/.openhuman/memory/
```

### Test 2: Check Obsidian sees the notes

1. Open Obsidian vault
2. Go to `00-Inbox/OpenHuman-Feed/`
3. Should see `github-*.md`, `slack-*.md`, `gmail-*.md` files

### Test 3: Query via MCP bridge

```bash
# Inside your vault's python env:
python
>>> from mcp_bridge import MCPBridge
>>> bridge = MCPBridge(vault_path="/vault")
>>> notes = await bridge.query_openhuman_feed(source="github")
>>> print(notes)
[{'source': 'github', 'title': 'Issue #42', ...}, ...]
```

---

## 🆘 Troubleshooting

### Q: Symlink not working on Windows
**A:** Use WSL, or manually set the vault path in OpenHuman UI settings.

### Q: OpenHuman not syncing after 20 mins
**A:** Check OpenHuman logs:
```bash
openhuman --log-level=debug
```

### Q: No notes appearing in vault
**A:** 
1. Verify symlink: `ls -la ~/.openhuman/memory`
2. Check OpenHuman is running: `ps aux | grep openhuman`
3. Manually trigger sync in OpenHuman UI if available
4. Check `~/.openhuman/.env` is correct

### Q: Git won't commit OpenHuman notes
**A:** Add this to `.gitignore`:
```
HYPERFOCUS_ZONE/00-Inbox/OpenHuman-Feed/
```
OpenHuman-synced notes shouldn't be version-controlled (ephemeral).

---

## 🔗 Resources

- **OpenHuman Docs:** https://docs.openhuman.io
- **GitHub Issues:** https://github.com/tinyhumansai/openhuman/issues
- **agentmemory Tracking:** https://github.com/tinyhumansai/openhuman/issues/2620
- **This Repo:** https://github.com/welshdog/BROski-Obsidian-Brain-for-HyperFocus-z0ne

---

## 🎉 Result

Your brain is now:
- ✅ **Unified** — GitHub, Gmail, Slack → one vault
- ✅ **Queryable** — MCP bridge searches across everything
- ✅ **Agent-aware** — Claude Code, Cursor, your agents all read the same context
- ✅ **Automatic** — No manual sync needed; OpenHuman polls every 20 mins
- ✅ **Organized** — PARA structure keeps things tidy
- ✅ **Timestamped** — Every note has metadata + created date
- ✅ **Linkable** — Obsidian wiki-links work across sources

**Nothing gets lost. Everything flows in. Your brain knows everything.**

---

> 🐶♾️ Built by @welshDog — Llanelli, Wales  
> *"Stop apologising for your brain. Start building."*

