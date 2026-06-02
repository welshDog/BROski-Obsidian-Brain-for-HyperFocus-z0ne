# 🧠 AIFS — AI File System

> **One contract. Real enforcement. Any tool. Full safety.**

AIFS is a folder-contract protocol that gives AI agents explicit, human-readable rules for every folder they touch. Built by welshDog × Perplexity, June 2026.

---

## What Is AIFS?

Every folder that AI touches declares its own rules. The AI reads the nearest contract first, obeys local rules before global ones, and **stops if the folder says hands off.**

No more AI wandering into the wrong folder. No more forgotten migrations. No more surprise deletes.

---

## The Three-Layer Contract

| File | Purpose | Audience |
|------|---------|----------|
| `AGENTS.md` | Behavior, safety, guardrails | AI agents |
| `folder.prompt.md` | Plain-English intent | Humans + AI |
| `manifest.toml` | Machine-readable policy | AI + CI/CD |

Plus four power-ups:
- `.ailock` — hard stop file (like `.gitignore` for AI)
- `context.md` — current sprint state
- `TRUST.md` — per-agent trust tiers
- `ttl.toml` — time-expiring rules

---

## Discovery Order

1. `AGENTS.md` → behavior first
2. `manifest.toml` → policy second
3. `folder.prompt.md` → context third
4. Parent contract → inherit if missing
5. Global defaults → tool fallback

---

## Resolution Rules

- `MUST NOT` > `MAY` — deny by default
- `read_only = true` blocks ALL writes
- Local > Parent > Global
- Subfolders: stricter only
- When unclear: **STOP & ASK**

---

## Files in This Repo

```
AIFS/
├── AIFS_Specification_v0.3.md   ← Full spec
├── aifs_validator.py             ← CLI validator
├── aifs_watcher.py               ← Real-time enforcement daemon 🔥
├── templates/
│   ├── AGENTS.md
│   ├── manifest.toml
│   ├── folder.prompt.md
│   ├── .ailock
│   ├── context.md
│   └── TRUST.md
└── .github/workflows/
    └── aifs-validate.yml         ← GitHub Action CI
```

---

## Quick Start

```bash
# Validate all contracts in a repo
python AIFS/aifs_validator.py check .

# Start the real-time watcher daemon
python AIFS/aifs_watcher.py watch . --discord-webhook=YOUR_WEBHOOK

# Check a specific action
python AIFS/aifs_validator.py check . --action=create --folder=docs --ext=.md
```

---

## The Hyper Vision

```
AIFS Core (spec + validator)         ✅ Built
AIFS Watcher (real-time daemon)      ✅ Built
AIFS Hub (cloud dashboard)           🔜 Next
AIFS Registry (shared contracts)     🔜 Future
```

---

*Built by welshDog × Perplexity — Llanelli, Wales 🏴󠁧󠁢󠁷󠁬󠁳󠁧 — June 2026*

> Stop apologising for your brain. Start building.
