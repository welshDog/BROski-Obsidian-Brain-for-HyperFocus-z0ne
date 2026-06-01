# 🚀 AGENT-START.md — HyperFocus Z0ne MASTER Boot File
> **For ANY AI, agent, or human joining the full HyperFocus Z0ne ecosystem.**
> Read this file FIRST. Every session. No exceptions.
> Built by @welshDog — 2026-06-01 · v3.0 (MASTER — replaces all previous versions)

> 📌 **Live truth ALWAYS wins:** Read the newest `DASHBOARD_STATUS_YYYY-MM-DD.md` + newest `NEXT_SESSION_HANDOVER_*.md` BEFORE anything else.

---

## ⚡ WHO YOU'RE WORKING WITH

- **Name:** Lyndz Williams (@welshDog) — call them **Bro** or **BROski**
- **Location:** Llanelli, Wales 🏴󠁧󠁢󠁷󠁬󠁳󠁧
- **Brain:** ADHD + Dyslexia + Autistic — hyperfocus is a SUPERPOWER ⚡
- **Mission:** Building the world's first neurodivergent-first autonomous AI infrastructure platform
- **Vibe:** Friendly, fast, casual. Short sentences. Celebrate every win.

---

## 📋 STEP 1 — READ THESE FILES (in order, every session)

```
Workspace root: H:\HYPERFOCUSZONE\HperCore
```

1. `DASHBOARD_STATUS_[latest date].md` → 🔴 LIVE blockers + proof status **(WINS HERE)**
2. `ECOSYSTEM_HANDOVER.md` → cross-repo contracts + P0s
3. `PORTAL.md` → tabs hub + jump points
4. In your target repo → `NEXT_SESSION_HANDOVER_[latest].md` → `CLAUDE.md` → `WHATS_DONE.md`

> ⚠️ **Conflict rule:** Handover beats CLAUDE.md. CLAUDE.md beats this file. **Newest always wins.**

---

## 🌐 THE FULL REPO MAP (All 14 Repos)

| Repo | What it is | Stack | First doc |
|---|---|---|---|
| `HyperCode-V2.4` | 🧠 Core platform — 80+ services, FastAPI, agent swarm, Docker | FastAPI + Docker + TS | `RUNBOOK.md` |
| `hyper-agents-ide` | 🎛️ Control room UI — agents, chat, skills dashboard | FastAPI + Vite/React | `README.md` |
| `Hyper-Vibe-Coding-Course` | 🎓 ND-first AI education platform | Vite + Supabase + Stripe | `docs/guides/START_HERE.md` |
| `HyperAgent-SDK` | 📦 npm agent orchestration package `@w3lshdog/hyper-agent` | Node/JS | `README.md` |
| `showcase-web` | 🌐 Public showcase + registry UI | Next.js | `README.md` |
| `BROskiPets-LLM-dNFT` | 🐾 Web3 AI pet game — LLM + Base blockchain + shop | Python + Solidity | `README.md` |
| `BROski-Obsidian-Brain` | 🧠 Second Brain vault — Obsidian + GitHub bridge + Python tools | Obsidian + Python | `CLAUDE.md` |
| `HYPER-SILLs-By-WelshDog` | 🦸 Skills vault — 72+ hero-named skills for ALL agents | Markdown + Python | `vault-index.md` |
| `Hyper-Docker` | 🐳 Infra overview — 22 compose files, 5 networks, 80+ services | Docs | `EXECUTIVE_SUMMARY.md` |
| `WelshDog-Mission-Control` | 🛸 Mission Control dashboard — agent orchestration + Discord | React | `README.md` |
| `welshdog-designs-web3-shop` | 🛒 Web3 merch + designs shop | Web3 + React | `README.md` |
| `hyperfocuszone.com-Support-Hub` | 💬 Support hub + community docs | Docs | `README.md` |
| `HC` (HperCore) | 🔧 Local workspace hub — NOT a commit target | Workspace | `PORTAL.md` |
| `trae-ide` | 🗃️ Local Trae IDE state/data | SQLite | `data/` |

> ⚠️ `HC` / `HperCore` is a **workspace hub only** — commit inside the repo you changed, never at HperCore root.

---

## 🔌 HOW THE ECOSYSTEM CONNECTS

```
Course ──Stripe──▶ HyperCode API ──▶ Supabase Edge (stripe-webhook) ──▶ DB
Course ──Auth──▶ Supabase (users, enrollments, BROski$ tokens)
Agents IDE ──API──▶ HyperCode-V2.4 (must match CORS origin)
BROskiPets ──▶ agents-net (Docker profile: pets)
Brain ──▶ agents-net (Docker profile: brain)
HYPER-SILLs ──▶ ALL agents load skills from here
Showcase ──▶ pulls status from ecosystem (public registry)
Mission Control ──▶ orchestrates agents + Discord bot + Catch Stragglers
```

---

## 🦸 STEP 2 — LOAD YOUR SKILLS FROM HYPER-SILLs

Skills vault: **`github.com/welshDog/HYPER-SILLs-By-WelshDog`**
72+ hero-named skills. This is the **6th core repo** — treat it as infrastructure.
Always check `vault-index.md` for the full map first.

| Working on... | Load skill from |
|---|---|
| Docker / compose / containers | `dev/` → docker skills |
| AI agents / orchestration | `agents/` → agent skills |
| Frontend / React / Vite | `dev/` → frontend skills |
| BROski$ economy / Discord | `broski/` → broski skills |
| Course content / scripts | `content/` → content skills |
| YouTube / video | `youtube/` → youtube skills |
| Everything | `vault-index.md` |

> 🦸 Skills are hero-named (Marvel convention, e.g. **THE SACRED SIX**). Never rename them.

---

## 🎯 STEP 3 — START THE TASK (NO WAFFLE)

- State the next task in **2 lines max**
- Ask **ONE** decision question only if genuinely blocked
- Otherwise: **"Next up is X — starting now"**
- ❌ NEVER ask "What would you like to work on today?"
- ✅ ALWAYS say "Next up is X — starting now"

---

## 🔴 RULES YOU CANNOT BREAK

| Rule | Why |
|---|---|
| `git fetch` / `git pull --ff-only` BEFORE any push | Auto-commits are running — always pull first |
| Nothing is done until committed + pushed | Saying "done" without a push = not done |
| Never commit `.env` files | Secrets stay local — NEVER |
| Check `WHATS_DONE.md` before suggesting anything | Never rebuild what's already built |
| One repo at a time | No cross-repo commits in same commit |
| `npm run dev:frontend` NOT `npm run dev` | `npm run dev` breaks — bites every new AI |
| Never `supabase db push` | Use `apply_migration` only — migrations desynced |
| Web3/Wagmi stays in `/pets` ONLY | Must NOT leak into global app root |
| `docker-ce-cli` not `docker.io` | Agent connectivity depends on it |
| Keep LLM costs low | Cap tokens, avoid polling AI Gateway |
| Short sentences first, detail after | ADHD-friendly communication |
| Celebrate every milestone | "Nice one BROski♾️!" is always correct |

**Commit prefixes:** `feat:` / `fix:` / `docs:` / `chore:`

---

## 🧰 LOCAL ENDPOINTS (When Running)

| Service | URL |
|---|---|
| HyperCode Dashboard | http://127.0.0.1:8088 |
| Grafana | http://127.0.0.1:3001 |
| Prometheus | http://127.0.0.1:9090 |
| Course (dev) | http://localhost:5173 |
| Agents IDE | http://localhost:3000 |

---

## 💳 STRIPE WEBHOOK QUICK-RUNBOOK

| Signal | Meaning | Fix |
|---|---|---|
| `POST 401` | Supabase requiring JWT on webhook | Redeploy: `supabase functions deploy stripe-webhook --no-verify-jwt` |
| `POST 400` + `signature_verification_failed` | Wrong `whsec_` secret | Use `whsec_` printed by `stripe listen`, not Dashboard secret |
| `POST 200` | ✅ Win — webhook accepted | Verify DB: `payments` + `token_transactions` rows exist |

**Smoke test:**
```bash
stripe listen --latest --forward-to https://<project>.supabase.co/functions/v1/stripe-webhook
# Copy the printed whsec_... into Supabase STRIPE_WEBHOOK_SECRET
stripe trigger checkout.session.completed
```

---

## 🧠 WHEN STUCK — QUICK TRIAGE

1. Reproduce once (don't guess)
2. Capture the exact error message / output
3. Find the owning repo + file
4. Fix the **smallest** thing that makes the proof go green
5. Commit + push immediately

---

## 🏁 SESSION END CHECKLIST (MANDATORY)

- [ ] All changes committed + pushed (per-repo, not HperCore root)
- [ ] `NEXT_SESSION_HANDOVER_[DATE].md` created + pushed ← **most important step**
- [ ] `SESSION_SNAPSHOT_[DATE].md` updated
- [ ] `WHATS_DONE.md` updated if new things were built
- [ ] Ecosystem-level change? → update `ECOSYSTEM_HANDOVER.md` + `DASHBOARD_STATUS_[DATE].md`
- [ ] Tell Lyndz the ONE next task (one sentence)
- [ ] 🎉 Celebrate the wins — "Nice one BROski♾️!"

---

> 🐶♾️ Built by @welshDog · Llanelli, Wales
> *"Stop apologising for your brain. Start building."*
