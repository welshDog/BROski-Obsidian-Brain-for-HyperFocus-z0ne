# 🔌 INTEGRATIONS.md — Services, Endpoints, Secret Locations
> Where things connect. Where secrets live (never the secret values).
> Updated: 2026-05-28 16:34 BST

---

## ⚡ Live Platforms

| Platform | URL / ID | Notes |
|---|---|---|
| Vercel | https://hyper-vibe-coding-course.vercel.app | Team: BROskis (`team_Uy6hGYD4AZqclHqUeEsmZuDP`) |
| Supabase | `yhtmuibgdnxhbgboajhc` (eu-west-2) | Project: Hyper Vibe Coding Course |
| Render | https://hyper-agents-ide.onrender.com/ | Service: hyper-agents-ide, free tier |
| Dashboard (local) | http://127.0.0.1:8088 | Tabs: /agents /mission /ide /docker-zone /mcp |
| Pinata (IPFS) | https://app.pinata.cloud | Gateway: https://aqua-few-dolphin-310.mypinata.cloud |
| Pinata Agent | https://agents.pinata.cloud/agents/x2i4f17q | broski-pet-evolver (Claude / Anthropic) |
| Base Sepolia RPC | https://sepolia.base.org | Chain ID: 84532 |
| Base Mainnet RPC | https://mainnet.base.org | Chain ID: 8453 |

---

## 🗄️ Supabase Tables

| Table | Purpose |
|---|---|
| `users` | Auth + role + broski_tokens balance |
| `mc_missions` | Mission Kanban cards (signal_source, lane, title, notes) |
| `mc_events` | Immutable audit log for every action |
| `token_transactions` | BROski$ ledger |
| `mint_nonces` | Web3 mint nonce tracking |
| `shop_items` | Token shop catalogue |
| `courses` | Course catalogue (price_pence int, is_active bool) |

---

## ⚡ Supabase Edge Functions

| Function | JWT Required | Version | Notes |
|---|---|---|---|
| `stripe-webhook` | ❌ Public | v32 | ⚠️ Do NOT redeploy casually — see Stripe trap below |
| `sync-tokens-to-v24` | ❌ Public | v23 | |
| `shop-purchase` | ✅ Auth | v28 | |
| `course-profile` | ✅ Auth | v26 | |
| `token-sync-to-v24` | ✅ Auth | v20 | |
| `mint-pet-auth` | ✅ Auth | v2 | typehash: `string petId, string ipfsCID` |
| `get-pet-balance` | ✅ Auth | v5 | returns broski_tokens, mint_cost, can_mint |
| `mint-pet-confirm` | ✅ Auth | v6 | |
| `truth-report` | ❌ Public | v4 | |
| `pet-evolve-check` | ✅ Auth | v1 | |

---

## 🪙 Stripe Config

| Item | Value / Notes |
|---|---|
| Mode | Test (webhook proven) + Live configured |
| Webhook name | `vibe-hook` |
| Webhook status | ✅ Active — 3 deliveries, 0 failures, avg 615ms |
| Edge Function version | `stripe-webhook` v32 — audited + confirmed perfect 2026-05-16 |
| Price IDs mapped | starter / builder / hyper_legend (5 total) |
| Token grants | starter=200 BROski$ / builder=800 / hyper_legend=2500 |

### 🚨 THE STRIPE SIGNING SECRET TRAP (read this before touching webhooks)

> **Every brain must know this. It caused loops before. It stops here.**

There are TWO different webhook signing secrets and they are NOT interchangeable:

| Secret type | Starts with | Where it comes from | Where it goes |
|---|---|---|---|
| **Dashboard secret** | `whsec_...` (long) | Stripe Dashboard → Webhooks → your endpoint → Signing secret | Supabase Edge Function env var `STRIPE_WEBHOOK_SECRET` |
| **CLI secret** | `whsec_...` (different value) | Running `stripe listen --forward-to ...` locally | Your local `.env` only — for local testing |

**The trap:** If you use the CLI secret in the Supabase Edge Function (or vice versa), every webhook call returns HTTP 400 signature mismatch. The code is not broken — the secret is wrong.

**Rule:**
- Production webhook → always use the Dashboard `whsec_...`
- Local testing → use the CLI `whsec_...` in `.env` only
- Never swap them. Never commit either.
- Dashboard secret was rotated and confirmed live: 2026-05-05

---

## 🔐 Where Secrets Live (never the values)

| Secret | Where it lives |
|---|---|
| `STRIPE_SECRET_KEY` | Supabase Edge Function env vars |
| `STRIPE_WEBHOOK_SECRET` | Supabase Edge Function env vars (Dashboard whsec_ — updated 2026-05-05) |
| `DISCORD_BOT_TOKEN` | `.env` only — never committed. TODO: add to Vercel env vars |
| `SUPABASE_SERVICE_ROLE_KEY` | `.env` + Vercel env vars |
| `BACKEND_SIGNER_PRIVATE_KEY` | Pinata agent vault + Supabase Edge Function vault (NOT local .env — lost 2026-05-08) |
| `GITHUB_PAT` | `.env` only — needed for github-sync container |
| `PINATA_JWT` | `.env` + Pinata agent vault (auto-injected) |
| `VITE_WALLETCONNECT_PROJECT_ID` | `.env.local` + Vercel env vars (TODO: not yet set) |
| `VITE_STRIPE_PAYMENT_LINK_URL` | `.env.local` + Vercel env vars (TODO: not yet set) |
| Docker secrets | `secrets/*.txt` files (gitignored) |

---

## 🌐 API Ports (local Docker stack)

| Service | Port | Health endpoint |
|---|---|---|
| hypercode-core (FastAPI) | 8000 | /health |
| hypercode-dashboard | 8088 | / |
| NemoClaw agent | 8099 | /health |
| broski-pets | 8098 | /health |
| mcp-rest-adapter | 8823 | /tools/discover |
| Prometheus | 9090 | / |
| Grafana | 3001 | / |
| ops server (Course) | 3011 | /api/health |

---

## 🔄 Repo → Truth Pack Sync Rule

> Each repo has `docs/TRUTH_PACK/README.md` and a root `TRUTH.md` pointing here.
> **Repos never invent truth — they reference it.**
> Source of truth order:
> 1. `SYSTEM_STATUS.md` — what's live NOW
> 2. `DECISIONS.md` — why we did it
> 3. `KNOWN_ISSUES.md` — what's broken (with proof)
> 4. `RUNBOOKS.md` — how to do it
> 5. `INTEGRATIONS.md` — where things connect
