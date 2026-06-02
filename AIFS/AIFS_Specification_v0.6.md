# AIFS — AI File System Specification v0.6

> **The Folder Contract Protocol for AI Agents**
> Contracts are now cryptographically signed with Ed25519. Tampered = blocked.

Built by welshDog × Perplexity | June 2026

---

## What Changed in v0.6

- **Ed25519 signing** — every `manifest.toml` can be signed by the human author
- **Tamper detection** — if a contract is modified after signing, AI tools see `TAMPERED` and block
- **CI integration** — `verify-all` exits `1` if any contract is tampered (GitHub Actions ready)
- **Zero extra deps for verification** — only `cryptography` pip package needed
- Signature is embedded in `[signature]` section of `manifest.toml` — no separate file

---

## How It Works

```
Human writes manifest.toml
    ↓
python aifs_sign.py sign ./folder
    ↓
Ed25519 signs canonical JSON of policy sections
    ↓
Signature stored in [signature] block of manifest.toml
    ↓
AI tool reads contract → calls verify → VALID or TAMPERED
    ↓
TAMPERED = hard block (same as .ailock match)
```

---

## Signature Block

```toml
[signature]
key_id     = "aifs-welshdog-2026"
algorithm  = "Ed25519"
signed_at  = "2026-06-02T22:30:00Z"
signed_by  = "welshDog"
sig_hex    = "<128 hex chars>"
public_key = "<64 hex chars>"
digest     = "<sha256 of canonical policy JSON>"
```

---

## Verification Rules

| Status | Meaning | AI Action |
|--------|---------|----------|
| `valid` | Signature matches | Trust and obey |
| `unsigned` | No signature | Obey, warn human |
| `tampered` | Modified after signing | **HARD BLOCK** |
| `error` | Corrupt data | **HARD BLOCK** |

---

## CLI Reference

| Command | What It Does |
|---------|--------------|
| `keygen` | Generate Ed25519 keypair |
| `sign <folder>` | Sign manifest.toml |
| `verify <folder>` | Verify — exit 1 if tampered |
| `inspect <folder>` | Print contract + sig details |
| `sign-all <root>` | Sign every manifest.toml in repo |
| `verify-all <root>` | Verify all — CI-ready |
| `revoke <folder>` | Remove signature |

---

## Roadmap

| Phase | Status |
|-------|---------|
| v0.1 — Core spec | ✅ Done |
| v0.2 — Validator + CI | ✅ Done |
| v0.3 — Watcher + TTL + TRUST + .ailock | ✅ Done |
| v0.4 — MCP resource integration | ✅ Done |
| v0.5 — AIFS Hub dashboard | ✅ Done |
| v0.6 — Cryptographic contract signing | ✅ Done |
| v1.0 — AIFS Registry (shareable contracts) | 🔜 Next |

---

*Built by welshDog × Perplexity — Llanelli, Wales 🏴󠁧󠁢󠁷󠁬󠁳󠁧 — June 2026*
