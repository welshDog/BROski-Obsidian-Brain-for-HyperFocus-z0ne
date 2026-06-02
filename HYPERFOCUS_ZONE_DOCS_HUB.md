# 🧠 HYPERFOCUS Z0ne — Master Docs Hub
> **Single source of truth for every repo in the ecosystem**
> Last Updated: 2026-06-02 | Maintained in: `BROski-Obsidian-Brain`
> Rule: Each repo keeps its own docs. This hub links to them — never duplicates.

---

## ⚡ Start Here (Every Session)

| Priority | File | What it does |
|---|---|---|
| 🔴 1 | [ECOSYSTEM_HANDOVER.md](../HperCore/ECOSYSTEM_HANDOVER.md) | Root workspace map + P0 issues |
| 🔴 2 | [NEXT_SESSION_HANDOVER_2026-06-02.md](./NEXT_SESSION_HANDOVER_2026-06-02.md) | TODAY's brain handover |
| 🔴 3 | [AGENT-START.md](./AGENT-START.md) | Load skills + start task |
| 🟡 4 | [WHATS_DONE.md](./WHATS_DONE.md) | Full history — never rebuild what's here |
| 🟡 5 | [PORTAL.md](./PORTAL.md) | Hub navigation index |

---

## 🏗️ THE FULL HYPERFOCUS Z0ne — Repo Map

### 🔴 TIER 1 — Daily Drivers (Active Build)

| Repo | What it is | Stack | Start command | Key docs |
|---|---|---|---|---|
| [Hyper-Vibe-Coding-Course](https://github.com/welshDog/Hyper-Vibe-Coding-Course) | ⭐ CURRENT FOCUS — Neurodivergent AI course platform | Vite + React + Supabase + Stripe | `cd frontend && npm run dev:frontend` | README, CLAUDE.md, WHATS_DONE.md, rewrites/NEXT_SESSION_HANDOVER |
| [HyperCode-V2.4](https://github.com/welshDog/HyperCode-V2.4) | Core platform — 32 Docker containers, FastAPI, agent swarm | FastAPI + Docker + Python | See `RUNBOOK.md` | CLAUDE.md, CLAUDE_CONTEXT.md, docs/START_HERE.md |
| [BROski-Obsidian-Brain-for-HyperFocus-z0ne](https://github.com/welshDog/BROski-Obsidian-Brain-for-HyperFocus-z0ne) | 🧠 THIS REPO — persistent knowledge base + AI tools | Python + Obsidian | N/A (brain/data) | AGENT-START.md, WHATS_DONE.md, vault-index |
| [HyperAgent-SDK](https://github.com/welshDog/HyperAgent-SDK) | npm package for AI agent orchestration | Node/JS | `npm i` then CLI | README, CLAUDE_CONTEXT.md, hyper-agent-spec.json |

---

### 🟡 TIER 2 — Active Supporting Repos

| Repo | What it is | Stack | Key docs | Status |
|---|---|---|---|---|
| [hyper-agents-ide](https://github.com/welshDog/hyper-agents-ide) | Control room UI/API — HYPER Agents IDE | Python + UI | README | ⚠️ P0-3: API URL mismatch |
| [BROskiPets-LLM-dNFT](https://github.com/welshDog/BROskiPets-LLM-dNFT) | AI pets + Web3 shop + Solidity contracts | Python + Solidity + Docker | README | 🔧 Active — /pets route live |
| [showcase-web](https://github.com/welshDog/showcase-web) | Public landing + ecosystem showcase hub | Next.js | README | 🟡 Needs demo section |
| [WelshDog-Mission-Control](https://github.com/welshDog/WelshDog-Mission-Control) | Mission Control dashboard + CatchStragglers | React | README | 🔜 Sprint 4 wiring |
| [HYPER-SILLs-By-WelshDog](https://github.com/welshDog/HYPER-SILLs-By-WelshDog) | Hyper Skills vault — 72 rescued skills | Markdown + Python | vault-index.md | ⚡ Raiding in progress |

---

### 🟢 TIER 3 — Ecosystem / Infrastructure

| Repo | What it is | Stack | Notes |
|---|---|---|---|
| [HC](https://github.com/welshDog/HC) | HyperCode root / config hub | Various | Check WHATS_DONE before touching |
| [Hyper-Docker](https://github.com/welshDog/Hyper-Docker) | Docker/Compose ecosystem — 22 compose files | Docker | EXECUTIVE_SUMMARY.md is the bible |
| [hyperfocuszone.com-Support-Hub](https://github.com/welshDog/hyperfocuszone.com-Support-Hub-) | Support hub + issue tracker | GitHub Issues | Check for open P0s |
| [trae-ide](https://github.com/welshDog/trae-ide) | Local Trae IDE state/data | SQLite | Data store only — no code here |
| [wsl](https://github.com/welshDog/wsl) | WSL config + setup scripts | Shell/PowerShell | Windows dev env |
| [welshdog-designs-web3-shop](https://github.com/welshDog/welshdog-designs-web3-shop) | Web3 shop frontend | Web3/JS | Linked to BROskiPets |

---

## 📚 Key Docs by Category

### 🤖 Agent & AI Docs
| Doc | Location | What it does |
|---|---|---|
| AGENT-START.md | Brain root | Load skills + session kickoff |
| AGENT-START-SDK.md | Brain root | SDK-specific agent start |
| AGENT-START-PETS.md | Brain root | Pets-specific agent start |
| CLAUDE.md | Each repo root | Sacred rules per repo — read first |
| CLAUDE_CONTEXT.md | HyperCode, SDK | Deep context snapshot |
| Merge_CLAUDE.md | Brain root | Merged context for multi-repo sessions |
| vault-index.md | Brain root | 72 rescued skills + 37 catalogued |

### 🏗️ Architecture & Planning
| Doc | Location | What it does |
|---|---|---|
| ECOSYSTEM_HANDOVER.md | HperCore root | Full ecosystem map + P0 tasks |
| ANALYSIS_AND_ROADMAP.md | Brain root | Macro roadmap |
| MASTER_INTEGRATION_PLAN.md | Hyper-Docker | Phase 1-4 consolidation plan |
| UPGRADE_COMPLETE_SUMMARY.md | Brain root | Latest infra upgrade status |
| HYPERFOCUS_ZONE_BUILD_v2.2.md | Brain root | Zone build spec v2.2 |
| Brain-Constellation.md | Brain root | Visual brain map |

### 📋 Session & Handover Docs
| Doc | Location | What it does |
|---|---|---|
| NEXT_SESSION_HANDOVER_2026-06-02.md | Brain root | TODAY — always wins |
| WHATS_DONE.md | Every repo | Never rebuild what's here |
| SESSION_SNAPSHOT files | rewrites/ | Sprint history per session |
| Dashboard.md | Brain root | Live ops dashboard |
| Focus-Command-Center.md | Brain root | ADHD focus command centre |

### 🐳 DevOps & Infrastructure
| Doc | Location | What it does |
|---|---|---|
| EXECUTIVE_SUMMARY.md | Hyper-Docker | 80+ services, 22 compose files |
| COMPOSE_QUICK_REFERENCE.md | Hyper-Docker | Daily ops command cheat sheet |
| DEPLOYMENT_READINESS.md | Hyper-Docker | 100+ item pre-deploy checklist |
| FULL_HEALTH_CHECK_REPORT.md | Hyper-Docker | Latest health audit (8.8/10) |
| AIFS.md | Brain root | AI File System docs |
| AIFS-LAUNCH.ps1 | Brain root | PowerShell launch script for AIFS |

---

## 🔴 P0 — Current Blockers (Fix These First)

| Priority | Issue | Repo | Status |
|---|---|---|---|
| P0-1 | Revenue loop end-to-end (Stripe → webhook → DB) | Vibe Course + HyperCode | ⏳ In progress |
| P0-2 | Course Pricing must never dead-end | Vibe Course | ✅ Fallback shipped |
| P0-3 | Agents IDE "Failed to load agents/chat/skills" | hyper-agents-ide | 🔧 CORS/URL mismatch |
| P0-4 | HyperCode CRITICAL containers + credential errors | HyperCode-V2.4 | 🔧 Auth flow broken |
| P0-5 | Wire CatchStragglers into Mission Control | WelshDog-Mission-Control | 🔜 Sprint 4 todo |

---

## 🛠️ Tools & Stack Summary

| Tool | Purpose | Notes |
|---|---|---|
| **Trae IDE** | Windows IDE — main coding environment | PowerShell terminal, WSL2 optional |
| **AIFS Hub** | AI File System dashboard (port 7331) | Live at `http://127.0.0.1:7331/` |
| **Obsidian** | Brain vault UI | Reads this repo directly |
| **Supabase** | Course DB + edge functions | Project: `yhtmuibgdnxhbgboajhc` |
| **Vercel** | Course frontend deployment | `hyper-vibe-coding-course.vercel.app` |
| **Docker** | All backend infra | Use `docker-ce-cli` NOT `docker.io` |
| **NotebookLM** | 53-source course brain | Add latest handover each session |

---

## 🚀 How to Start Any Session

1. **Read this file** — you're here ✅
2. **Read** `NEXT_SESSION_HANDOVER_[latest].md` — live state always wins
3. **Check** `WHATS_DONE.md` — never rebuild what exists
4. **Pick ONE repo** — commit inside it, not at HperCore root
5. **Push to GitHub** — nothing is done until it's committed

---

## 🌟 THE MISSION

> *"Stop apologising for your brain. Start building."*
> Transform permission-seekers into Meta-Architects.
> ADHD + Dyslexic + Autistic minds — this is a SUPERPOWER not a limitation.

---

*Auto-maintained by BROski Brain 🧠 | welshDog/BROski-Obsidian-Brain-for-HyperFocus-z0ne*
