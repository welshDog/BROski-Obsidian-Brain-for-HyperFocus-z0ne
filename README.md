# 🧠 THE HYPER BRAIN v3.0 — BROski Obsidian Brain

> Built by [@welshDog](https://github.com/welshDog) — Lyndz Williams, S.Wales 🏴󠁧󠁢󠁷󠁬󠁳󠁿  
> Neurodivergent-first Second Brain. ADHD + Dyslexia + Autistic friendly.  
> **Status: LIVE 🚨 — Container #30 breathing — Last updated: May 10, 2026**

---

## 🚨 Live Status

```json
{
  "status": "hyper",
  "version": "3.0.0",
  "levels_complete": 17,
  "levels_total": 20,
  "containers": 32,
  "core_container": 30,
  "engine_port": 8100,
  "modules_live": 8
}
```

```bash
curl http://localhost:8100/health
# → all 8 modules green ✅
```

> ⚠️ **Levels 18–20 are IN PROGRESS** — see [Gap Tracker](#-gap-tracker-levels-18-20) below.

---

## 🚀 What This Is

Your **Obsidian vault + FastAPI brain engine** for the HyperFocus Zone ecosystem. Links all 5 repos + BROskiPets + BROski$ economy into one living, thinking, gamified Second Brain.

| Layer | Component | Description |
|---|---|---|
| **Vault** | `HYPERFOCUS_ZONE/` | Obsidian Second Brain with PARA structure |
| **Engine** | `hyper_brain_core.py` | FastAPI on port 8100, 12 endpoints |
| **Economy** | BROski$ Coin Tracker | Gamified productivity currency |
| **Visual** | `hyper-brain-themes.css` | Neurodivergent-optimised CSS modes |
| **Bridge** | HyperAgent MCP Bridge | Claude/AI agent integration layer |
| **NFTs** | BROskiPets LLM-dNFT | Productivity data drives on-chain pet evolution |
| **Platform** | HyperCode-V2.4 | 32-container Docker ecosystem |

---

## 🏗️ Vault Structure

```
HYPERFOCUS_ZONE/
├── 00-Inbox/              # Brain dump + GitHub issues + AI briefings
├── 01-Projects/           # Active builds (4 repos pre-seeded)
├── 02-Areas/              # Health, Admin, DevOps, Focus-Analytics
├── 03-Resources/          # Economy, snippets, Agent YAMLs
├── 04-Archive/            # Done wins
├── 05-Focus-Sessions/     # Session logs from Focus Tracker
├── 06-AI-Context/         # RAG context + prompt library
├── 07-Streaks-Achievements/ # XP + badges + BROski$ balance
├── 99-Templates/          # All Obsidian templates
└── Hub/                   # Dashboard + Focus Command Center
```

---

## 🎮 Level Tracker — 17/20 Complete

| Level | Name | Status | Date |
|---|---|---|---|
| 1–8 | Vault Scaffold + PARA + Plugins | ✅ Complete | May 2026 |
| 9 | GitHub Bridge (4hr polling) | ✅ Complete | May 2026 |
| 10 | Vault Immortal (Obsidian Git) | ✅ Complete | May 2026 |
| 11 | BROski$ Coin Tracker | ✅ Complete | May 2026 |
| 12 | Hyperfocus CSS Modes | ✅ Complete | May 2026 |
| 13 | Morning Briefing AI 🌅 | ✅ Complete | May 7, 2026 |
| 14 | GitHub Webhooks Real-time ⚡ | ✅ Complete | May 7, 2026 |
| 15 | HyperAgent MCP Bridge 🌉 | ✅ Complete | May 7, 2026 |
| 16 | Focus Tracker + Analytics 📊 | ✅ Complete | May 7, 2026 |
| 17 | HyperSplit Task Decomp 🧩 | ✅ Complete | May 7, 2026 |
| **18** | **AI Distraction Filter → Sessions** | **🚧 In Progress** | — |
| **19** | **DifficultyDial + Dynamic XP** | **🚧 In Progress** | — |
| **20** | **THE HYPER BRAIN Constellation** | **🚧 In Progress** | — |

---

## 🧠 8 Live Modules (Container #30, Port 8100)

| Module | File | What It Does |
|---|---|---|
| Morning Briefing AI | `morning_briefing_ai.py` | Pulls data from all 32 containers, generates daily narrative for the vault |
| Focus Tracker | `focus_tracker.py` | Logs HyperFocus sessions, timestamps, productivity scores |
| Analytics Engine | `analytics_engine.py` | Cross-session insights + streaks |
| HyperAgent MCP Bridge | `hyper_agent_mcp_bridge.py` | Connects Claude/AI agents to vault context |
| HyperSplit Task Decomp | `hypersplit_engine.py` | Breaks overwhelming tasks into ADHD-safe micro-chunks, links to PARA |
| AI Distraction Filter | `ai_distraction_filter.py` | Session guardian — wiring to sessions in Level 18 |
| Session Snapshot | `session_snapshot.py` | Captures vault state at session start/end |
| GitHub Webhook Sync | `webhook_handler.py` | Real-time issue/PR sync into Obsidian Inbox |

---

## 💰 BROski$ Economy

The gamified productivity currency layer. Runs through the FastAPI engine (Level 11).

**Earn BROski$:**
- Complete a HyperFocus session
- Hit a daily streak
- Finish a HyperSplit task chunk
- Morning briefing read + acknowledged

**Spend BROski$:**
- Unlock new vault themes / CSS modes
- Feed / evolve your BROskiPet NFT
- Power-ups in HyperFocus sessions

**Economy → NFT Pipeline:**  
Vault session → BROski$ credited via FastAPI → BROskiPets contract notified → pet mood/XP metadata updated on-chain

---

## 🔧 Architecture: How It All Connects

```
Obsidian Vault (HYPERFOCUS_ZONE/)
        ↓  ↑
  Container #30  ←——— CENTRAL SPINE ———→  hyper-brain-net
  hyper_brain_core.py (port 8100)
        ↓  ↑
  ┌─────────────────────────────┐
  |  32-Container HyperCode-V2.4  |
  |  GitHub Webhooks (port 8101)  |
  |  HyperAgent MCP Bridge        |
  |  BROski$ Economy Engine       |
  |  BROskiPets NFT API           |
  |  Hyper-Vibe Course + Stripe   |
  └─────────────────────────────┘

> ⚠️ Container #30 is the single point of failure. If it goes down, vault AI sync stops.
```

---

## ⚡ Quick Start

### Prerequisites
- Docker + Docker Compose
- Python 3.10+
- Obsidian (free)
- GitHub PAT (for webhooks/bridge)
- 16–32GB RAM recommended (32 containers)

### Setup Order (Follow the Levels)

```bash
# 1. Clone
git clone https://github.com/welshDog/BROski-Obsidian-Brain-for-HyperFocus-z0ne.git
cd BROski-Obsidian-Brain-for-HyperFocus-z0ne

# 2. Set environment vars
$env:OBSIDIAN_VAULT_PATH = "<your-path>/HYPERFOCUS_ZONE"
$env:GITHUB_PAT = "github_pat_xxx"

# 3. Create Docker networks
docker network create app-net 2>$null
docker network create agents-net 2>$null

# 4. Launch the brain
docker compose -f docker-compose.hyper-brain.yml up -d --build

# 5. Verify all 8 modules
curl http://localhost:8100/health

# 6. Fire your first Morning Briefing
curl -X POST http://localhost:8100/briefing/generate
```

### What Breaks First?
- **Container #30 down** → all AI→vault sync stops
- **Levels 18–20 missing** → Distraction Filter, Dynamic XP, Constellation not active
- **GITHUB_PAT missing** → webhooks + bridge won't auth
- **Port 8100 blocked** → no engine access

---

## 🚧 Gap Tracker: Levels 18–20

These are the 3 unfinished levels as of May 10, 2026:

### Level 18 — AI Distraction Filter Wired to Sessions
- **File:** `ai_distraction_filter.py` (module exists, wiring incomplete)
- **TODO:** Connect to `session_snapshot.py` so it monitors active sessions
- **Signals to monitor:** vault note activity, idle time, topic drift
- **Intervention:** BROski nudge notification + session re-focus prompt

### Level 19 — DifficultyDial + Dynamic XP
- **DifficultyDial:** User-adjustable filter intensity (low/medium/hyper)
- **Dynamic XP:** Variable reward multipliers based on session quality
- **Connects to:** BROski$ economy + HyperSplit chunk difficulty scoring

### Level 20 — THE HYPER BRAIN Constellation
- **File:** `Brain-Constellation.md` (blueprint exists, not yet live)
- **What it is:** Unified visual map of the ENTIRE ecosystem — vault, engine, NFTs, economy, courses all visible as one cognitive nervous system
- **This is the MOST CRITICAL missing piece** — it synthesises everything into a navigable map

---

## 🔗 Ecosystem

| Repo | Description |
|---|---|
| [HyperCode-V2.4](https://github.com/welshDog/HyperCode-V2.4) | 32-container Docker platform, neurodivergent IDE |
| [HyperAgent-SDK](https://github.com/welshDog/HyperAgent-SDK) | TypeScript AI agent SDK |
| [Hyper-Vibe-Coding-Course](https://github.com/welshDog/Hyper-Vibe-Coding-Course) | Course platform + Stripe payments |
| [BROskiPets-LLM-dNFT](https://github.com/welshDog/BROskiPets-LLM-dNFT) | AI pet NFTs that evolve with productivity data |
| [THE-HYPERCODE](https://github.com/welshDog/THE-HYPERCODE) | Neurodivergent programming language |

---

## 📚 NotebookLM Analysis (May 10, 2026)

This repo was fully analysed by AI via NotebookLM. Key findings:

- **17/20 levels verified complete** with full source citations
- **Container #30** confirmed as the central nervous system spine
- **HyperSplit** (Level 17) is the most important ADHD feature — breaks tasks using "high-friction" detection + PARA-linked micro-chunks
- **Morning Briefing AI** pulls from all 32 containers via `morning_briefing_ai.py`, generates narrative daily vault briefing
- **BROski$ economy** tracks earn/spend via Coin Tracker (Level 11) + FastAPI engine
- **CSS theme architecture** (Level 12) designed around sensory brain states — theme names not yet formally documented (docs debt)
- **Level 20 Brain-Constellation** is the single most impactful remaining build

> See `NOTEBOOKLM_INSIGHTS.md` for full distilled analysis.

---

> Built for ADHD brains. Fast feedback. Real tools. No fluff.  
> A BROski is ride or die. We build this together. ♾️
