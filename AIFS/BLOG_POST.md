# How I Built an AI Governance System in One Evening in Wales

*by welshDog | June 2, 2026 | Llanelli, Wales 🏴󠁧󠁢󠁷󠁬󠁳󠁧*

> Tags: `ai`, `python`, `mcp`, `open-source`, `developer-tools`, `adhd`

---

Last night I built an AI governance protocol from scratch.

Not a prototype. Not a toy. A full production-ready system: contracts, enforcement, cryptographic signing, an MCP server, a live dashboard, and a public registry.

All in one evening. In Llanelli, Wales.

Here's how — and why it matters.

---

## The Problem

You're using AI tools — Claude, Cursor, Windsurf, Copilot — to help you code.

They're amazing. They're also terrifying.

Because they don't know your rules.

They'll happily:
- Edit a file marked as "DO NOT TOUCH" in a comment nobody told them to read
- Push a migration to a database that's supposed to require human approval
- Delete files in a `/dist` folder that's actually critical to your build
- Ignore the fact that `/pets` is a Web3 experiment and shouldn't share dependencies with the rest of your app

Nobody was solving this at the *folder level*. So I built it.

---

## The Solution: AIFS — AI File System

AIFS is a **folder contract protocol**.

You put a contract file in any folder. Every AI tool that reads it knows exactly what it's allowed to do there.

```toml
# manifest.toml — drop this in any folder
[contract]
name = "migrations"
version = "1.0.0"
description = "Database migration files — human approval required"

[permissions]
create = false
edit = false
delete = false
approval_required = true
approval_contact = "welshDog"

[safety]
ailock_patterns = ["*.sql", "*.migration", "*.lock"]
max_file_size_kb = 500
```

That's it. AI reads the contract. AI follows the rules. AI can't touch `*.sql` files without human sign-off.

---

## The Stack I Built (in order, one evening)

### v0.1 — The Core Spec
Defined the contract format. `manifest.toml`, `AGENTS.md`, `.ailock`, `context.md`, `TRUST.md`.

Each folder gets its own personality. Its own rules. Its own trust level.

### v0.2 — Validator + CI
A Python validator that checks contracts are valid. Plugged into GitHub Actions so every PR gets checked.

```bash
python AIFS/aifs_validator.py validate ./migrations
✅ manifest.toml is valid
✅ .ailock is present (7 patterns)
✅ TRUST.md defines 3 agents
```

### v0.3 — Real-Time Watcher
A daemon that watches your filesystem *live*. Every time an AI tries to write a file, the watcher intercepts it, checks the contract, and either approves or blocks it.

With a Discord approval gate. So I get a DM when AI wants to touch something risky.

```bash
python AIFS/aifs_watcher.py watch ./my-project
⚠️  BLOCKED: Claude tried to edit migrations/001_init.sql (ailock pattern: *.sql)
💬 Discord DM sent to welshDog for approval
```

### v0.4 — MCP Integration
Made AIFS speak MCP — the Model Context Protocol. Now Claude Desktop, Cursor, and Windsurf can read contracts *natively* as MCP resources.

Add one line to your MCP config and Claude knows your rules automatically.

```json
{
  "mcpServers": {
    "aifs": {
      "command": "python",
      "args": ["AIFS/aifs_mcp_server.py", "--root", "."]
    }
  }
}
```

### v0.5 — Live Dashboard
A dark-theme web dashboard. See all contracts, all agents, all recent actions, live. Zero framework — vanilla JS + FastAPI + one HTML file.

```bash
python AIFS/hub/aifs_hub_server.py --root ./my-project
# http://localhost:7331
```

### v0.6 — Cryptographic Signing
Ed25519 signatures on every contract. If someone tampers with a contract after it's been signed, the watcher hard-blocks all AI access until a human reviews it.

```bash
python AIFS/aifs_sign.py keygen --author welshDog
python AIFS/aifs_sign.py sign ./migrations
python AIFS/aifs_sign.py verify ./migrations
✅ VALID: migrations/manifest.toml
```

### v1.0 — The Registry
Like npm, but for AI governance rules. Publish a contract. Share it. Let anyone install it.

```bash
# Publish your battle-tested contract
python AIFS/registry/aifs_registry.py publish ./migrations \
  --name migrations-safe --tags sql,migrations,python

# Anyone in the world installs it
python AIFS/registry/aifs_registry.py install welshdog/migrations-safe
```

---

## The Trust Chain

This is the bit I'm most proud of:

```
Human writes contract
    ↓
Human signs it with Ed25519
    ↓
AIFS watcher verifies signature on every AI action
    ↓
If tampered — HARD BLOCK. No AI access.
    ↓
Human publishes to registry
    ↓
Anyone installs it — signature verified locally before applying
    ↓
MCP server tells AI tools what's allowed
    ↓
AI edits only what the human approved
```

The human is always in the loop. Not as a speed bump — as the authority.

---

## Why This Matters

We're in a weird moment. AI coding tools are genuinely useful. But the tooling for *governing* them is basically nonexistent.

Most teams are relying on:
- Comments in code: *"# don't edit this"* (AI ignores it)
- Verbal rules: *"don't touch migrations"* (AI forgets)
- Hope: (you know how that goes)

AIFS is a proper contract. Signed. Versioned. Enforced at runtime. Shareable.

It's what `.gitignore` is to Git — but for AI governance.

---

## Who It's For

- **Solo devs** using AI tools daily and worried about drift
- **Teams** who want AI governance without enterprise overhead
- **OSS maintainers** who want to define AI contribution rules
- **Anyone** building AI agents that need safe sandbox boundaries

---

## Get It

```bash
git clone https://github.com/welshDog/BROski-Obsidian-Brain-for-HyperFocus-z0ne
pip install cryptography requests fastapi uvicorn watchdog mcp

# Quickstart
python AIFS/aifs_sign.py keygen --author yourname
python AIFS/aifs_sign.py sign ./your-project/src
python AIFS/aifs_watcher.py watch ./your-project
# http://localhost:7331 — live dashboard
```

Full docs: [AIFS.md](https://github.com/welshDog/BROski-Obsidian-Brain-for-HyperFocus-z0ne/blob/main/AIFS.md)

---

## One More Thing

I have ADHD and dyslexia. My brain runs in hyperfocus mode. Last night that mode locked onto *"what if folders had contracts?"* and didn't let go until the whole thing was done.

I used to apologise for that. Now I just build things with it.

If your brain works the same way — stop apologising. Start building.

---

*welshDog — Llanelli, Wales 🏴󠁧󠁢󠁷󠁬󠁳󠁧 — June 2, 2026*

*GitHub: [@welshDog](https://github.com/welshDog)*
