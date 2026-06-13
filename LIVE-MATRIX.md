# 🗺️ LIVE MATRIX — Hyperfocus Zone Ecosystem
> Last updated: 2026-06-13 | Source: Perplexity Hyper Audit Session
> ⚠️ This is the SINGLE SOURCE OF TRUTH for what is actually live vs test vs experimental.

---

## 🟢 LIVE (Production-ready, real users)

| Feature | Repo(s) | Mode | Notes |
|---|---|---|---|
| Course Platform — Modules 1–10 | Hyper-Vibe-Course | 🟢 LIVE | All 10 modules rewritten, Sprint 4 anon signup live since 2026-05-19 |
| Anonymous Student Signup Flow | Hyper-Vibe-Course + Supabase | 🟢 LIVE | 33 green anon-flow tests passing |
| Stripe Payments (TEST mode only) | Hyper-Vibe-Course | 🟡 TEST | Webhook verified in TEST. Old docs claiming LIVE are STALE — ignore them |
| Mission Control Frontend | HyperCode-V2.4 | 🟢 LIVE | Dashboard loads, broski-bot connected |
| Catch Stragglers Overlay | HyperCode-V2.4 | 🟢 LIVE (UI) | Overlay in Mission Control is live. DM router not fully smoke-tested |
| BROski Discord Bot | HyperCode-V2.4 / agents/broski-bot | 🟢 LIVE | discord.py==2.4.0, entrypoint: python -u -m cogs.bot |
| Hyper Brain — Modules 1–17 | BROski-Obsidian-Brain | 🟢 LIVE | Morning Briefing, Focus Tracker, HyperSplit, MCP Bridge, Session Snapshot, Analytics, GitHub Webhook all running |
| HYPER-SILLs Skills Vault (72 skills) | HYPER-SILLs-By-WelshDog | 🟢 LIVE | Source of truth for all AI skill loading |
| Obsidian PARA Vault | BROski-Obsidian-Brain | 🟢 LIVE | Vault + GitHub bridge working |
| Prometheus + Grafana Observability | HyperCode-V2.4 | 🟢 LIVE (local) | Local URLs confirmed working. No cloud alerting yet |

---

## 🟡 IN PROGRESS (Partially built, NOT fully reliable)

| Feature | Repo(s) | Mode | Notes |
|---|---|---|---|
| Catch Stragglers — DM Router | HyperCode-V2.4 | 🟡 IN PROGRESS | `DISCORDBOTTOKEN` needs wiring to Vercel env. mcevents migration pending |
| Stripe LIVE Mode | Hyper-Vibe-Course | 🟡 PENDING | Only TEST mode verified. LIVE key swap needs explicit test run before enabling |
| Hyper Brain Level 18 — AI Distraction Filter | BROski-Obsidian-Brain | 🟡 IN PROGRESS | `ai_distraction_filter.py` exists (8.5KB). Not wired to session_snapshot.py events yet |
| Hyper Brain Level 19 — DifficultyDial + XP | BROski-Obsidian-Brain | 🟡 IN PROGRESS | `difficulty_dial.py` exists (2.6KB). XP multiplier not wired to BROski economy yet |
| Hyper Brain Level 20 — Brain Constellation | BROski-Obsidian-Brain | 🟡 IN PROGRESS | `constellation_builder.py` + `graph_builder.py` exist. No live endpoint / UI yet |
| HyperAgent-SDK npm package | HyperAgent-SDK | 🟡 LIVE (alpha) | `@w3lshdog/hyper-agent` published. No versioned API contracts or load tests yet |
| CI/CD Pipelines | All repos | 🟡 PARTIAL | Vercel handles Course. VS Code tasks exist. No GitHub Actions across all repos |
| Supabase Schema Boundary (Course vs MC) | Hyper-Vibe-Course + HyperCode-V2.4 | 🟡 RISK | Single Supabase project. No automated schema diff checks yet |

---

## 🔴 EXPERIMENTAL / NOT LIVE (Blueprint only)

| Feature | Repo(s) | Mode | Notes |
|---|---|---|---|
| BROskiPets-LLM-dNFT — XP loop | BROskiPets-LLM-dNFT | 🔴 EXPERIMENTAL | Web3 pet game exists. XP → pet evolution mapping not defined or safe-gated yet |
| Agent Prompt Contracts / Evals | All repos | 🔴 MISSING | No central prompt spec or eval checklists per agent type |
| Infra Health Single Dashboard | HyperCode-V2.4 | 🔴 MISSING | Prometheus/Grafana wired locally but no single service-map dashboard |
| Pre-commit Security Hooks | All repos | 🔴 MISSING | Rules written in docs but NOT enforced by automation |
| Discord DM Observability | HyperCode-V2.4 | 🔴 MISSING | No Prometheus metrics for DM send attempts, failures, or retries |
| Meta-Architect Agent Ops Layer | All repos | 🔴 BLUEPRINT | Concept exists in docs. No implementation yet |

---

## 🔒 SACRED RULES (Never Break)

```
✔ docker-ce-cli — NEVER docker.io for socket agents
✔ from app.X import Y — NEVER from backend.app.X  
✔ .env files — NEVER committed to git
✔ Stripe webhook — rate-limit EXEMPT, always
✔ Python indent — 4 spaces, NEVER 3, NEVER mixed
✔ Redis DB 1=cache, DB 2=rate limits. NEVER mix.
✔ npm run dev:frontend (NOT npm run dev)
✔ broski-bot — discord.py==2.4.0. NEVER py-cord.
✔ Bot entrypoint — python -u -m cogs.bot. NEVER python main.py
```

---

## 📋 Update Protocol
- Update this file at the START and END of every AI session
- Format: add new rows, change emoji status, note the date
- Never delete rows — move deprecated items to a `## ⚫ DEPRECATED` section
