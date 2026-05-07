# 🧠 THE HYPER BRAIN v3.0 — BROski Obsidian Brain

> Built by [@welshDog](https://github.com/welshDog) — Lyndz Williams, S.Wales 🏴󠁧󠁢󠁷󠁬󠁳󠁠
> Neurodivergent-first Second Brain. ADHD + Dyslexia + Autistic friendly.
> **Status: LIVE 🚨 — Container #30 breathing — May 7, 2026**

---

## 🚨 Live Status

```json
{"status":"hyper","version":"3.0.0","level":20,"containers":30}
```

`curl http://localhost:8100/health` → all 8 modules green ✅

---

## 🚀 What This Is

Your **Obsidian vault + FastAPI brain engine** for the HyperFocus Zone ecosystem.
Links all 5 repos + BROskiPets + BROski$ economy into one living, thinking brain.

- **Vault** (`HYPERFOCUS_ZONE/`) — Obsidian Second Brain with PARA structure
- **Engine** (`hyper_brain_core.py`) — FastAPI on port 8100, 12 endpoints
- **8 modules** all live: briefings, focus tracking, webhooks, MCP, analytics, HyperSplit, distraction filter, snapshots

---

## 🏗️ Vault Structure

```
HYPERFOCUS_ZONE/
├── 00-Inbox/        # Brain dump + GitHub issues + AI briefings
├── 01-Projects/     # Active builds (4 repos pre-seeded)
├── 02-Areas/        # Health, Admin, DevOps, Focus-Analytics
├── 03-Resources/    # Economy, snippets, Agent YAMLs
├── 04-Archive/      # Done wins
├── 05-Focus-Sessions/ # Session logs
├── 06-AI-Context/   # RAG + prompt library
├── 07-Streaks-Achievements/ # XP + badges
├── 99-Templates/    # All templates
└── Hub/             # Dashboard + Command Center
```

---

## 🎮 Level Tracker

- [x] **Level 1–8** — Vault scaffold + PARA + plugins ✅
- [x] **Level 9** — GitHub bridge (4hr polling) ✅
- [x] **Level 10** — Vault immortal (Obsidian Git) ✅
- [x] **Level 11** — BROski$ Coin Tracker ✅
- [x] **Level 12** — Hyperfocus CSS Modes ✅
- [x] **Level 13** — Morning Briefing AI 🌅 ✅ *May 7*
- [x] **Level 14** — GitHub Webhooks real-time ⚡ ✅ *May 7*
- [x] **Level 15** — HyperAgent MCP Bridge 🌉 ✅ *May 7*
- [x] **Level 16** — Focus Tracker + Analytics 📊 ✅ *May 7*
- [x] **Level 17** — HyperSplit Task Decomp 🧩 ✅ *May 7*
- [ ] **Level 18** — AI Distraction Filter wired to sessions
- [ ] **Level 19** — DifficultyDial + Dynamic XP
- [ ] **Level 20** — THE HYPER BRAIN Constellation

---

## ⚡ Quick Start

```powershell
git clone https://github.com/welshDog/BROski-Obsidian-Brain-for-HyperFocus-z0ne.git
cd BROski-Obsidian-Brain-for-HyperFocus-z0ne

# Set env vars
$env:OBSIDIAN_VAULT_PATH = "H:/BROski-Obsidian-Brain-for-HyperFocus-z0ne/HYPERFOCUS_ZONE"
$env:GITHUB_PAT = "github_pat_xxx"

# Create networks + fire up
docker network create app-net 2>$null
docker network create agents-net 2>$null
docker compose -f docker-compose.hyper-brain.yml up -d --build

# Verify
curl http://localhost:8100/health

# First morning briefing
curl -X POST http://localhost:8100/briefing/generate
```

---

## 🔗 Ecosystem

- [HyperCode-V2.4](https://github.com/welshDog/HyperCode-V2.4) — Docker platform, 32 containers
- [HyperAgent-SDK](https://github.com/welshDog/HyperAgent-SDK) — TypeScript SDK
- [Hyper-Vibe-Coding-Course](https://github.com/welshDog/Hyper-Vibe-Coding-Course) — Course + Stripe
- [BROskiPets-LLM-dNFT](https://github.com/welshDog/BROskiPets-LLM-dNFT) — AI pet NFTs

---

> *Built for ADHD brains. Fast feedback. Real tools. No fluff.*
> *A BROski is ride or die. We build this together. ♾️*
