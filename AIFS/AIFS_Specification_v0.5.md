# AIFS — AI File System Specification v0.5

> **The Folder Contract Protocol for AI Agents**
> Now with a live web dashboard — see every contract, lock, and in-flight file in one view.

Built by welshDog × Perplexity | June 2026

---

## What Changed in v0.5

- **AIFS Hub Dashboard** (`hub/index.html` + `hub/aifs_hub_server.py`)
- **Live auto-refresh** every 10 seconds
- **6 panels:** Overview, Folders, In-Flight, Locks, Trust, Audit Log
- **FastAPI backend** with 8 REST endpoints
- **Zero build step** — single HTML file, vanilla JS, dark theme
- Run: `python AIFS/hub/aifs_hub_server.py --root .`
- Open: `http://localhost:7331`

---

## Dashboard Panels

| Panel | What It Shows |
|-------|---------------|
| 📊 Overview | Stat cards: contracts, in-flight, locks, agents, read-only folders, audit entries |
| 📁 Folders | Every folder with a contract — permissions, read-only status, in-flight count |
| ⚠️ In-Flight | All files protected by context.md across the whole project |
| 🚫 Locks | Every .ailock pattern — hard stops at a glance |
| 👤 Trust | Agent trust tiers from all TRUST.md files |
| 📝 Audit Log | CHANGELOG.ai.md entries — who touched what, when |

---

## API Endpoints

| Endpoint | Returns |
|----------|---------|
| `GET /` | Dashboard HTML |
| `GET /api/summary` | Overview stats |
| `GET /api/contracts` | All resolved contracts |
| `GET /api/in-flight` | All in-flight files across project |
| `GET /api/locks` | All .ailock patterns |
| `GET /api/trust` | All agent trust tiers |
| `GET /api/audit` | Recent audit log entries |
| `GET /api/contract/{path}` | Single folder contract |

---

## Full Stack Overview

```
AIFS Core Files (in your folders)
    manifest.toml, AGENTS.md, .ailock, context.md, TRUST.md
           ↓
aifs_watcher.py (real-time enforcement daemon)
           ↓ logs to CHANGELOG.ai.md
aifs_mcp_server.py (MCP resources for AI tools)
           ↓ aifs://folder/{path}, check_action, get_in_flight
aifs_hub_server.py (FastAPI REST + dashboard)
           ↓
http://localhost:7331 (you, looking at everything)
```

---

## Roadmap

| Phase | Status |
|-------|---------|
| v0.1 — Core spec | ✅ Done |
| v0.2 — Validator + CI | ✅ Done |
| v0.3 — Watcher + TTL + TRUST + .ailock | ✅ Done |
| v0.4 — MCP resource integration | ✅ Done |
| v0.5 — AIFS Hub dashboard | ✅ Done |
| v0.6 — Cryptographic contract signing | 🔜 Next |
| v1.0 — AIFS Registry (shareable contracts) | 🔜 Future |

---

*Built by welshDog × Perplexity — Llanelli, Wales 🏴󠁧󠁢󠁷󠁬󠁳󠁧 — June 2026*
