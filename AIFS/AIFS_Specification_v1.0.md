# AIFS — AI File System Specification v1.0

> **The Folder Contract Protocol for AI Agents — Complete.**
> From a folder file to a global registry. The whole stack is here.

Built by welshDog × Perplexity | June 2026 | Llanelli, Wales 🏴󠁧󠁢󠁷󠁬󠁳󠁧

---

## What AIFS Is

AIFS is a **folder contract protocol** for AI agents.
It lets you define, enforce, sign, monitor and share rules about what AI tools
are allowed to do in every folder of your project.

No AI goes rogue. No file gets deleted by accident. No migration gets auto-pushed.
Every action is checked against a contract. Every contract is signed by a human.
Every contract can be shared with the world.

---

## The Full Stack

| Layer | File | What It Does |
|-------|------|--------------|
| **Contracts** | `manifest.toml`, `AGENTS.md`, `.ailock`, `context.md`, `TRUST.md` | Define the rules per folder |
| **Validator** | `aifs_validator.py` | Check contract structure, run in CI |
| **Signer** | `aifs_sign.py` | Ed25519 sign + verify contracts |
| **Watcher** | `aifs_watcher.py` | Real-time enforcement daemon + Discord approvals |
| **MCP Server** | `aifs_mcp_server.py` | Expose contracts as MCP resources |
| **Hub** | `hub/aifs_hub_server.py` | Live web dashboard |
| **Registry** | `registry/aifs_registry.py` | Publish, discover, install contracts |
| **Registry Server** | `registry/registry_server.py` | Self-hostable registry API |

---

## Registry — Publish. Discover. Install. Trust.

```bash
# Publish
python AIFS/registry/aifs_registry.py publish ./src \
  --name fastapi-src --tags fastapi,python,backend

# Search
python AIFS/registry/aifs_registry.py search migrations

# Install
python AIFS/registry/aifs_registry.py install welshdog/migrations-safe --target ./migrations

# Verify
python AIFS/registry/aifs_registry.py verify welshdog/migrations-safe
```

---

## The Trust Chain

```
Human writes contract
    ↓
Human signs with Ed25519 (aifs_sign.py)
    ↓
Human publishes to registry (aifs_registry.py publish)
    ↓
Anyone installs it (aifs_registry.py install)
    ↓
Signature verified locally before applying
    ↓
aifs_watcher.py enforces rules in real-time
    ↓
aifs_mcp_server.py tells AI tools what’s allowed
    ↓
AI edits only what the human approved
```

---

## Complete Roadmap — Done.

| Phase | Status |
|-------|---------|
| v0.1 — Core spec | ✅ |
| v0.2 — Validator + CI | ✅ |
| v0.3 — Watcher + TTL + TRUST + .ailock | ✅ |
| v0.4 — MCP resource integration | ✅ |
| v0.5 — AIFS Hub dashboard | ✅ |
| v0.6 — Cryptographic contract signing | ✅ |
| v1.0 — AIFS Registry | ✅ |

**AIFS is complete. The protocol is production-ready.**

---

## What’s Next (Community)

- Host the public registry at `aifs-registry.hyperfocuszone.com`
- Seed it with contracts for: FastAPI, Next.js, React, migrations, docs, tests
- Submit AIFS to awesome-mcp lists and MCP server registries
- Write a blog post: *“How I built an AI governance system in one evening in Wales”*
- Open to community contributions via GitHub

---

## One-Page Summary

> Put `manifest.toml` in a folder. AI knows the rules.
> Put `.ailock` in a folder. AI cannot touch those files. Ever.
> Put `context.md` in a folder. AI knows what’s in-flight right now.
> Sign it with `aifs_sign.py`. Anyone can verify it wasn’t tampered.
> Publish it with `aifs_registry.py`. Anyone can install your rules.
> Watch it live in the Hub dashboard. See every action in real-time.

---

*Built in one evening. Llanelli, Wales. June 2026.*
*AIFS — The AI File System Protocol — is complete.*
