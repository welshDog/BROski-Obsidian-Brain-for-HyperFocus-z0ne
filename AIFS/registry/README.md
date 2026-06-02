# 🌍 AIFS Registry — v1.0

> **Publish. Discover. Install. Trust.**
> The public registry for AIFS folder contracts.

Like npm for AI governance rules. One command to share a contract with the world.
One command to install a battle-tested contract into your project.

---

## Quick Start

```bash
pip install cryptography requests fastapi uvicorn

# Publish your contract
python AIFS/registry/aifs_registry.py publish ./src --name "fastapi-src" --tags fastapi,python,backend

# Search for contracts
python AIFS/registry/aifs_registry.py search fastapi

# Install a contract
python AIFS/registry/aifs_registry.py install welshdog/fastapi-src --target ./my-project/src

# Verify a published contract
python AIFS/registry/aifs_registry.py verify welshdog/fastapi-src

# Browse by author
python AIFS/registry/aifs_registry.py list --author welshdog
```

---

## Commands

| Command | What It Does |
|---------|--------------|
| `publish <folder>` | Sign + publish contract to registry |
| `search <query>` | Search contracts by name, tag, or description |
| `install <name>` | Download + apply contract to a target folder |
| `verify <name>` | Verify a registry contract’s signature |
| `list` | Browse contracts — filter by author, tag, language |
| `info <name>` | Full contract details + signature info |
| `unpublish <name>` | Remove your contract from the registry |
| `login` | Authenticate with the registry |

---

## Contract Naming

```
{author}/{contract-name}

Examples:
  welshdog/fastapi-src
  welshdog/migrations-safe
  welshdog/react-components
  community/nextjs-strict
```

---

## Self-Hosted Registry

```bash
# Run your own registry server
python AIFS/registry/registry_server.py --port 7332

# Point CLI at it
python AIFS/registry/aifs_registry.py search fastapi --registry http://localhost:7332
```

---

## Registry Entry Format

```json
{
  "name": "welshdog/fastapi-src",
  "author": "welshDog",
  "description": "Safe contract for FastAPI source folders",
  "tags": ["fastapi", "python", "backend"],
  "version": "1.0.0",
  "published_at": "2026-06-02T22:30:00Z",
  "public_key": "<hex>",
  "signature_valid": true,
  "downloads": 42,
  "contract": { ... }
}
```

---

## Trust Model

- Every published contract **must be signed** with Ed25519 (v0.6 aifs_sign.py)
- The registry stores the **public key** with the contract
- Anyone who installs it can **verify the signature locally** before applying
- Tampered contracts are **rejected at install time**
- Authors can **revoke** contracts at any time

---

## The Full AIFS Stack

```
Your folders ── manifest.toml, AGENTS.md, .ailock, context.md, TRUST.md
aifs_sign.py ── Ed25519 sign + verify
aifs_validator.py ─ contract structure validation
aifs_watcher.py ── real-time enforcement daemon
aifs_mcp_server.py ─ MCP resources for AI tools
hub/aifs_hub_server.py ─ live dashboard
registry/aifs_registry.py ─ publish + install contracts
registry/registry_server.py ─ self-hosted registry API
```

---

*AIFS v1.0 — Built by welshDog × Perplexity — Llanelli, Wales 🏴󠁧󠁢󠁷󠁬󠁳󠁧 — June 2026*
