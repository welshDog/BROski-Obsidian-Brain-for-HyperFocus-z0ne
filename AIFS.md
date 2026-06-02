# 🧠 AIFS — AI File System

> **The Folder Contract Protocol for AI Agents.**
> Define, enforce, sign, monitor and share rules about what AI tools are allowed to do in every folder of your project.

Built by welshDog × Perplexity | June 2026 | Llanelli, Wales 🏴󠁧󠁢󠁷󠁬󠁳󠁧

---

## ⚡ Quick Start

```bash
# 1. Clone the brain
git clone https://github.com/welshDog/BROski-Obsidian-Brain-for-HyperFocus-z0ne

# 2. Install deps
pip install cryptography requests fastapi uvicorn watchdog

# 3. Add a contract to your folder
cp AIFS/templates/manifest.toml ./my-project/src/

# 4. Sign it
python AIFS/aifs_sign.py keygen --author yourname
python AIFS/aifs_sign.py sign ./my-project/src

# 5. Start the watcher
python AIFS/aifs_watcher.py watch ./my-project

# 6. Open the dashboard
python AIFS/hub/aifs_hub_server.py --root ./my-project
# http://localhost:7331

# 7. Connect to Claude / Cursor (add to MCP config)
# See AIFS/mcp.json

# 8. Publish to registry
python AIFS/registry/aifs_registry.py login
python AIFS/registry/aifs_registry.py publish ./my-project/src --name my-src
```

---

## 📊 The Full Stack

| Layer | File | What It Does |
|-------|------|--------------|
| Contracts | `manifest.toml`, `AGENTS.md`, `.ailock`, `context.md`, `TRUST.md` | Rules per folder |
| Validator | `aifs_validator.py` | CI contract validation |
| Signer | `aifs_sign.py` | Ed25519 sign + verify |
| Watcher | `aifs_watcher.py` | Real-time enforcement + Discord |
| MCP Server | `aifs_mcp_server.py` | AI tools read contracts natively |
| Dashboard | `hub/aifs_hub_server.py` | Live web UI |
| Registry | `registry/aifs_registry.py` | Publish + install contracts |

---

## 🛡️ Core Contract Files

| File | Purpose |
|------|---------|
| `manifest.toml` | Policy: create/edit/delete rules, approval required, TTL |
| `AGENTS.md` | Human-readable rules for AI agents |
| `.ailock` | Hard-stop patterns — files AI can NEVER touch |
| `context.md` | Live sprint state: active task, in-flight files |
| `TRUST.md` | Per-agent trust tiers: FULL / EDIT_ONLY / READ_ONLY / BLOCKED |
| `folder.prompt.md` | Intent statement loaded as AI context |

---

## ✅ Roadmap — Complete

| Version | Feature | Status |
|---------|---------|--------|
| v0.1 | Core spec | ✅ |
| v0.2 | Validator + CI | ✅ |
| v0.3 | Watcher + TTL + TRUST + .ailock | ✅ |
| v0.4 | MCP resource integration | ✅ |
| v0.5 | Hub dashboard | ✅ |
| v0.6 | Cryptographic contract signing | ✅ |
| v1.0 | AIFS Registry | ✅ |

---

## 🌍 Registry

```bash
# Find community contracts
python AIFS/registry/aifs_registry.py search fastapi

# Install a battle-tested contract
python AIFS/registry/aifs_registry.py install welshdog/migrations-safe --target ./migrations

# Share yours
python AIFS/registry/aifs_registry.py publish ./src --name my-src --tags python,fastapi
```

---

## 📚 Specs

- [v0.3 Spec](AIFS/AIFS_Specification_v0.3.md)
- [v0.4 Spec — MCP](AIFS/AIFS_Specification_v0.4.md)
- [v0.5 Spec — Dashboard](AIFS/AIFS_Specification_v0.5.md)
- [v0.6 Spec — Signing](AIFS/AIFS_Specification_v0.6.md)
- [🌟 v1.0 Spec — Registry (Complete)](AIFS/AIFS_Specification_v1.0.md)

---

*AIFS — Built in one evening. Llanelli, Wales. June 2026.*
