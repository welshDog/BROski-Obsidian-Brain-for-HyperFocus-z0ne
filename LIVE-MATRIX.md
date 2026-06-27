# 🗺️ LIVE MATRIX — Hyperfocus Zone Ecosystem
> Last updated: 2026-06-27 | Brain Levels 1–21 live. Dependency/security health pass shipped (aiohttp 3.9.3→3.14.1).
> ⚠️ This is the SINGLE SOURCE OF TRUTH for what is actually live vs test vs experimental.

---

## 🟢 LIVE (Production-ready, real users)

| Feature | Repo(s) | Mode | Notes |
|---|---|---|---|
| Course Platform — Modules 1–10 | Hyper-Vibe-Course | 🟢 LIVE | All 10 modules rewritten, Sprint 4 anon signup live since 2026-05-19 |
| Anonymous Student Signup Flow | Hyper-Vibe-Course + Supabase | 🟢 LIVE | 33 green anon-flow tests passing |
| Mission Control Frontend | WelshDog-Mission-Control | 🟢 LIVE | v0.10.4 on Render + Vercel, broski-bot connected |
| Catch Stragglers — DM Router | WelshDog-Mission-Control | 🟢 LIVE | E2E smoke tested 2026-06-14. Discord DM delivered (msgId 1515509899868766238), audit rows written, 24h rate limit confirmed |
| Catch Stragglers Overlay | WelshDog-Mission-Control | 🟢 LIVE | UI overlay live. DM router confirmed end-to-end (2026-06-14) |
| Discord DM Observability | WelshDog-Mission-Control | 🟢 LIVE | `dm_send_attempt_total` + `dm_send_failure_total` Prometheus counters; `GET /metrics` scrape target (2026-06-14) |
| BROski Discord Bot | HyperCode-V2.4 / agents/broski-bot | 🟢 LIVE | discord.py==2.4.0, entrypoint: python -u -m cogs.bot |
| Hyper Brain — Modules 1–20 | BROski-Obsidian-Brain | 🟢 LIVE | Morning Briefing, Focus Tracker, HyperSplit, MCP Bridge, Session Snapshot, Analytics, GitHub Webhook, AI Distraction Filter (L18), DifficultyDial XP (L19), Constellation (L20) all running |
| Hyper Brain Level 18 — AI Distraction Filter | BROski-Obsidian-Brain | 🟢 LIVE | Wired to session_snapshot.py — snapshots capture live focus + distraction state (2026-06-14) |
| Hyper Brain Level 19 — DifficultyDial + XP | BROski-Obsidian-Brain | 🟢 LIVE | XP multiplier on session end, POSTed to HYPERCORE_API_URL/broski/award (fail-open), vault note uses multiplied values (2026-06-14) |
| Hyper Brain Level 20 — Brain Constellation | BROski-Obsidian-Brain | 🟢 LIVE | `GET :3302/constellation` D3 force-graph LIVE since 2026-06-11 |
| Hyper Brain Level 21 — Sensory Accessibility (B7) | BROski-Obsidian-Brain | 🟢 LIVE | `hyper-brain-themes.css` now honours OS `prefers-reduced-motion` + `sensory-low`/`sensory-calm` profiles + reusable `dyslexia-support` class. Closes bottleneck B7 (overload protection, transition aids). Synced to active Obsidian snippet (2026-06-27) |
| Brain Dependency/Security Health Pass | BROski-Obsidian-Brain | 🟢 LIVE | All 5 requirements.txt bumped off early-2024 pins; **aiohttp 3.9.3→3.14.1** (CVE fixes), FastAPI 0.110→0.138.1, pydantic 2.6→2.13.4; Dockerfiles 3.11→3.12-slim; fixed latent undeclared `requests` dep. 5 brain containers rebuilt + health-verified, 21/21 unit tests green (2026-06-27) |
| HYPER-SILLs Skills Vault (72 skills) | HYPER-SILLs-By-WelshDog | 🟢 LIVE | Source of truth for all AI skill loading |
| Obsidian PARA Vault | BROski-Obsidian-Brain | 🟢 LIVE | Vault + GitHub bridge working |
| Prometheus + Grafana Observability | HyperCode-V2.4 | 🟢 LIVE (local) | Local URLs confirmed working. No cloud alerting yet |

---

## 🟡 IN PROGRESS (Partially built, NOT fully reliable)

| Feature | Repo(s) | Mode | Notes |
|---|---|---|---|
| Stripe Payments (TEST mode only) | Hyper-Vibe-Course | 🟡 TEST | Webhook verified in TEST. LIVE key swap blocked on Companies House registration |
| HyperAgent-SDK npm package | HyperAgent-SDK | 🟡 LIVE (alpha) | `@w3lshdog/hyper-agent@0.4.0` published. No versioned API contracts or load tests yet |
| CI/CD Pipelines | All repos | 🟡 PARTIAL | Vercel handles Course. No GitHub Actions across all repos (billing lock) |
| Supabase Schema Boundary (Course vs MC) | Hyper-Vibe-Course + WelshDog-Mission-Control | 🟡 RISK | Single Supabase project. No automated schema diff checks yet |
| Drift Scan Agent Action | WelshDog-Mission-Control | 🟡 SOON | Last of the 6 Agent Actions — currently a SOON tile in MC |

---

## 🔴 EXPERIMENTAL / NOT LIVE (Blueprint only)

| Feature | Repo(s) | Mode | Notes |
|---|---|---|---|
| BROskiPets-LLM-dNFT — XP loop | BROskiPets-LLM-dNFT | 🔴 EXPERIMENTAL | EEPVengers LIVE on Base Sepolia testnet. XP → pet evolution mapping not safe-gated yet |
| BROskiPets relay + CDP key | BROskiPets-LLM-dNFT | 🔴 PENDING | `VITE_MINT_VIA_RELAY=true` + CDP key secret still to wire |
| Agent Prompt Contracts / Evals | All repos | 🔴 MISSING | No central prompt spec or eval checklists per agent type |
| Infra Health Single Dashboard | HyperCode-V2.4 | 🔴 MISSING | Prometheus/Grafana wired locally but no single service-map dashboard |
| Pre-commit Security Hooks | All repos | 🔴 MISSING | Rules written in docs but NOT enforced by automation |
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
✔ Brain containers — rebuild from HyperCode-V2.4 dir (NOT Brain repo standalone)
✔ DISCORD_BOT_TOKEN on Render — raw token only, no "Bot " prefix
```

---

## 📋 Update Protocol
- Update this file at the START and END of every AI session
- Format: add new rows, change emoji status, note the date
- Never delete rows — move deprecated items to a `## ⚫ DEPRECATED` section
