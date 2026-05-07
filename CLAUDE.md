# 🧠 CLAUDE.md — THE HYPER BRAIN v3.0
> Read this FIRST. Every session. No exceptions.
> Builder: @welshDog — Lyndz Williams, S.Wales 🏴󠁧󠁢󠁷󠁬󠁳󠁠
> Neurodivergent-first Second Brain — ADHD + Dyslexia + Autistic.

---

## 👤 Who You're Working With
- **Name:** Lyndz — call them "Bro" or "BROski"
- **Profile:** ADHD + Dyslexia + Autistic
- **Style:** Short bullets. Bold keys. Emojis. Why → How → Example. NEVER walls of text.
- **Energy:** Celebrate wins. Quick wins FIRST. Momentum > perfection.
- **Sacred Rule:** NEVER debate these rules. NEVER suggest removing them.

---

## 🏗️ This Repo — What It Is

**THE HYPER BRAIN v3.0** — Obsidian Second Brain + FastAPI engine for the HyperFocus Zone.

- Vault: `HYPERFOCUS_ZONE/` ← open THIS in Obsidian
- Local path: `H:\BROski-Obsidian-Brain-for-HyperFocus-z0ne`
- Brain API: `hyper_brain_core.py` → port 8100 (Container #30)
- Auto-commits every 10 mins via Obsidian Git

---

## 🌐 Cross-Repo Links — THE ECOSYSTEM

> Brain is the meta-layer. All 5 repos have CLAUDE.md. Read them for full context.

| Repo | CLAUDE.md | What it does |
|------|-----------|-------------|
| **[HyperCode-V2.4](https://github.com/welshDog/HyperCode-V2.4/blob/main/CLAUDE.md)** | [CLAUDE.md](https://github.com/welshDog/HyperCode-V2.4/blob/main/CLAUDE.md) | Docker platform, 32 containers, FastAPI core |
| **[HyperAgent-SDK](https://github.com/welshDog/HyperAgent-SDK/blob/main/CLAUDE.md)** | [CLAUDE.md](https://github.com/welshDog/HyperAgent-SDK/blob/main/CLAUDE.md) | TypeScript SDK, agent spec, CLI |
| **[Hyper-Vibe-Coding-Course](https://github.com/welshDog/Hyper-Vibe-Coding-Course/blob/main/CLAUDE.md)** | [CLAUDE.md](https://github.com/welshDog/Hyper-Vibe-Coding-Course/blob/main/CLAUDE.md) | Course frontend, Supabase, Stripe |
| **[BROskiPets-LLM-dNFT](https://github.com/welshDog/BROskiPets-LLM-dNFT/blob/main/CLAUDE.md)** | [CLAUDE.md](https://github.com/welshDog/BROskiPets-LLM-dNFT/blob/main/CLAUDE.md) | AI pet NFTs, LLM, on-chain XP |
| **THIS REPO (Brain)** | You are here 📍 | Second Brain, vault, AI layer |

---

## 🗂️ Vault Structure (PARA + extensions)

```
HYPERFOCUS_ZONE/
├── 00-Inbox/              # Brain dump + GitHub issues + AI captures
│   ├── GitHub/            # Auto-synced: issues + PRs
│   ├── Briefings/         # Morning briefings (morning_briefing_ai.py output)
│   └── AI-Capture/        # Voice → Whisper → notes (future)
├── 01-Projects/           # Active builds — 4 repos pre-seeded
├── 02-Areas/              # Health, Admin, DevOps, Focus-Analytics
├── 03-Resources/          # Economy table, snippets, Agent YAMLs
├── 04-Archive/            # Completed wins
├── 05-Focus-Sessions/     # Session logs (focus_tracker.py output)
├── 06-AI-Context/         # RAG chunks, prompt library
├── 07-Streaks-Achievements/ # XP, streak recovery, badges
├── 99-Templates/          # Daily, Project, Task, Morning Briefing, Focus-Session
└── Hub/                   # Dashboard + Focus Command Center
```

**SACRED RULE:** Notes ALWAYS go in correct folder. NEVER dump in repo root.

---

## 📦 Python Files — CANONICAL vs STUBS

> ⚠️  CRITICAL: Two sets of .py files exist. ROOT = real. scripts/ = stubs.

| Location | Status | Use for |
|----------|--------|--------|
| `/*.py` (repo root) | ✅ **CANONICAL v3.0** — full FastAPI, all modules wired | Docker build, running, editing |
| `scripts/*.py` (9 stubs) | ❌ **OLD STUBS** — 100-150 line skeletons, no real imports | **IGNORE / DELETE** |
| `scripts/github_to_obsidian.py` | ✅ **REAL** — GitHub sync script | GitHub → vault sync |
| `scripts/setup.ps1` | ✅ **REAL** — bootstrap | First-time setup |
| `scripts/setup_hyper_brain.ps1` | ✅ **REAL** — v3.0 bootstrap | Hyper Brain setup |

**When editing Python: ALWAYS edit root `.py` files. Never touch `scripts/*.py` stubs.**

---

## 🎮 Level Tracker — HONEST STATE

```
✅ Level 1–8   Vault scaffold + plugins + PARA
✅ Level 9    GitHub bridge (4hr polling) — scripts/github_to_obsidian.py
✅ Level 10   Vault immortal (Obsidian Git auto-commit)
✅ Level 11   BROski$ Coin Tracker (Dataview widget)
✅ Level 12   Hyperfocus CSS Modes (Focus/Calm/Hyper)
🔧 Level 13   Morning Briefing AI — CODE DONE (morning_briefing_ai.py)
                → NEEDS: docker up + test run
🔧 Level 14   GitHub Webhooks real-time — CODE DONE (github_webhook_server.py)
                → NEEDS: docker up + GitHub webhook registered
🔧 Level 15   HyperAgent AI Briefing — CODE DONE (mcp_bridge.py)
                → NEEDS: docker up + MCP port wired
🔧 Level 16   Focus Tracker + Analytics — CODE DONE (focus_tracker.py)
                → NEEDS: docker up + test /focus/start
🔧 Level 17   HyperSplit Task Decomp — CODE DONE (hyper_split.py)
                → NEEDS: docker up + test /hypersplit
⏳ Level 18   AI Distraction Filter — CODE DONE (ai_distraction_filter.py)
                → NEEDS: wiring to focus sessions
⏳ Level 19   DifficultyDial + Dynamic XP
⏳ Level 20   THE HYPER BRAIN Constellation (MCP mesh + RAG)
```

> 💡 Levels 13–17 are 80% done — all code exists. Just needs `docker up` + test.
> One command unlocks 5 levels at once.

---

## ⚡ Light The Engine (Level 13–17 in one go)

```powershell
# 1. Set env vars (in .env or terminal)
$env:OBSIDIAN_VAULT_PATH = "H:/BROski-Obsidian-Brain-for-HyperFocus-z0ne/HYPERFOCUS_ZONE"
$env:GITHUB_WEBHOOK_SECRET = "your_secret_here"
$env:GITHUB_PAT = "github_pat_xxx"

# 2. Create Docker networks if standalone
docker network create app-net 2>$null
docker network create agents-net 2>$null

# 3. FIRE IT UP
docker compose -f docker-compose.hyper-brain.yml up -d --build

# 4. Verify
curl http://localhost:8100/health
# → {"status":"hyper","level":20,"containers":30}

# 5. Trigger first morning briefing
curl -X POST http://localhost:8100/briefing/generate
# → Briefing drops into HYPERFOCUS_ZONE/00-Inbox/Briefings/
```

---

## 🐈 Claude Hyper Skills — What You CAN Do Here

### 🥇 Tier 1 — Auto (always do these)
1. **Note Filer** — correct folder always; never repo root
2. **Dataview Builder** — queries for Dashboard; always `LIMIT` + `SORT file.mtime DESC`
3. **Template Writer** — Templater syntax; YAML frontmatter with `created`, `tags`, `status`
4. **Script Fixer** — edit ROOT `.py` only; `os.environ.get()` for all env vars
5. **Docs Updater** — after every change: update WHATS_DONE + level tracker

### 🥈 Tier 2 — On Request
6. **Vault Cleaner** — detect/move misplaced files; enforce PARA
7. **GitHub → Task Notes** — issue JSON → BROski task template → 01-Projects/
8. **Morning Briefing** — POST /briefing/generate OR python morning_briefing_ai.py
9. **Focus Analytics** — weekly report from 05-Focus-Sessions/ → 02-Areas/Focus-Analytics/

### 🥉 Tier 3 — Advanced
10. **MCP Bridge Wiring** — vault as MCP source; config in 03-Resources/MCP/
11. **Webhook Server** — github_webhook_server.py → real-time vault notes
12. **HyperSplit** — POST /hypersplit → recursive micro-task tree in vault

---

## 🔑 Key Facts

```
Vault open path:    HYPERFOCUS_ZONE/
Local repo:         H:\BROski-Obsidian-Brain-for-HyperFocus-z0ne
Brain API:          http://localhost:8100
Docker file:        docker-compose.hyper-brain.yml (root — canonical)
GitHub sync:        python scripts/github_to_obsidian.py
PAT format:         github_pat_xxx (fine-grained)
CSS modes:          focus-mode | calm-mode | hyper-mode
BROski$ schema:     coins (int), xp (int), status, project
Docker mem cap:     hyper-brain = 256m
Obsidian Git:       10 min auto-commit, auto-push ON
MCP port:           8820 (not 8099 — corrected)
Redis:              DB4 for brain (DB1=cache, DB2=rate-limits in V2.4)
Canonical Python:   ROOT *.py files ONLY
Stubs location:     scripts/*.py — IGNORE
Networks needed:    app-net + agents-net (external, created by HyperCode stack)
```

---

## 🚫 What NEVER To Do

- ❌ NEVER edit `scripts/*.py` stubs — root is canonical
- ❌ NEVER create files in repo root (except README/CLAUDE/Dockerfile/compose/configs)
- ❌ NEVER hardcode paths or tokens
- ❌ NEVER commit `.env` or GITHUB_PAT
- ❌ NEVER wall of text — always chunk + bullet
- ❌ NEVER skip updating WHATS_DONE after shipping
- ❌ NEVER use `docker/` compose file — use root `docker-compose.hyper-brain.yml`

---

## 🚀 Current Sprint — Light The Engine

**Goal:** `docker compose up` → health green → Levels 13–17 unlocked

```
✅ Dockerfile fixed   — COPY *.py ./ (root, not scripts/)
✅ Compose fixed      — context: . | correct vault path | agents-net
✅ CLAUDE.md updated  — cross-repo links + honest level tracker
⏳ YOU: docker compose -f docker-compose.hyper-brain.yml up -d --build
⏳ YOU: curl http://localhost:8100/health
⏳ YOU: curl -X POST http://localhost:8100/briefing/generate
```

> *"The brain that changes itself is the brain that builds itself."*
> **THE HYPER BRAIN v3.0 — BROski♾️ builds the future.**
