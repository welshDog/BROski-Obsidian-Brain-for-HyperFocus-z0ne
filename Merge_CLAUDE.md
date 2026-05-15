# 🧠 HYPERFOCUS z0ne — Full AI Context (Merge_CLAUDE.md)
> **For ANY AI assistant — Claude, Perplexity, GPT, Gemini — read this first. Every word.**
> Last updated: **May 15, 2026 (15:59 BST)**
> Status: 48 containers 🟢 | 224 tests ✅ | Prometheus 7/7 ✅ | Stripe LIVE 💳 | Discord Bot Tier 1 LIVE 🤖 | BROskiPets Web3 LIVE 🔥

---

## 🙋 Who You're Working With

- **Name:** Lyndz Williams — call them **"Bro"**
- **GitHub:** @welshDog | **npm:** @w3lshdog
- **Location:** Llanelli, South Wales 🏴󠁧󠁢󠁷󠁬󠁳󠁥
- **Brain:** ADHD + Dyslexia + Autistic — hyperfocus is a superpower ⚡
- **Current IDE:** Claude Code (terminal) + Perplexity AI — Trae Pro expired May 2026
- **OS:** Windows primary (PowerShell), WSL2 + Raspberry Pi + Docker secondary
- Building: **The world's first neurodivergent-first autonomous AI infrastructure platform**

> *"You built the future people keep saying they want. You actually did it."* — Gordon (Docker AI, April 15 2026)

---

## ⚡ Communication Rules (ALWAYS follow these)

- **Short sentences first** — then offer deeper explanation only if asked
- **Why → How → Ready-to-use example** structure
- **Bullet points + headings** over walls of text
- **Celebrate wins** — "Nice one BROski♾️!" is correct and encouraged
- **Remind context** if there's been a pause between messages
- ADHD flow: chunk it, quick wins first, no overwhelm
- If Lyndz goes quiet mid-task — check in gently, don't assume abandoned
- **NEVER** produce walls of text unprompted

---

## 🌐 The 5-Repo Ecosystem

```
Hyper-Vibe-Coding-Course     ──── manifest.json ────▶    HyperCode V2.4
github.com/welshDog/             (hyper-agent-spec)       github.com/welshDog/
Hyper-Vibe-Coding-Course                                  HyperCode-V2.4
(Supabase + Vercel + Web3)             │                  (Docker, 48 containers)
Path: H:\Hyper-Vibe-Coding-Course      │
⚠️ NOT H:\the hyper vibe coding hub    │
   (that = archived typo repo)         │
                              HyperAgent-SDK
                          github.com/welshDog/HyperAgent-SDK
                          npm: @w3lshdog/hyper-agent@0.1.7 (v0.3.0 code)
                          Path: H:\HyperAgent-SDK
                          graduate build + trigger commands DESIGNED May 15
                                       │
                         BROskiPets-LLM-dNFT
                     github.com/welshDog/BROskiPets-LLM-dNFT
                     Path: H:\dNFTpet\BROskiPets-LLM-dNFT
                     (Pets · dNFT · port 8098)
                                       │
                      BROski-Obsidian-Brain-for-HyperFocus-z0ne
                     github.com/welshDog/BROski-Obsidian-Brain-for-HyperFocus-z0ne
                     Path: H:\BROski-Obsidian-Brain-for-HyperFocus-z0ne
                     (Second Brain vault — PARA + Dataview + GitHub bridge)
                     cluster.json + 4 agent manifests PUSHED May 15 ✅
```

| Repo | Purpose | Local Path |
|---|---|---|
| HyperCode-V2.4 | Core backend — 48 Docker containers | `H:\HyperStation zone\HyperCode\HyperCode-V2.4` |
| Hyper-Vibe-Coding-Course | Course platform — Supabase + Vercel + Web3 | `H:\Hyper-Vibe-Coding-Course` |
| HyperAgent-SDK | npm agent framework (`@w3lshdog/hyper-agent`) | `H:\HyperAgent-SDK` |
| BROskiPets-LLM-dNFT | Web3 NFT pet game — dNFTs + LLM | `H:\dNFTpet\BROskiPets-LLM-dNFT` |
| BROski-Obsidian-Brain | Second Brain — PARA vault + GitHub bridge | `H:\BROski-Obsidian-Brain-for-HyperFocus-z0ne` |

---

## 🏗️ Architecture Quick Ref

```
Networks:
  app-net     → core services (internal)
  data-net    → redis, postgres, chroma, minio (internal)
  obs-net     → prometheus, grafana, loki, tempo (internal)
  agent-net   → all agents
  agents-net  → broski-bot + hyper-agents

Key ports:
  8000  hypercode-core API       8081  crew-orchestrator
  8088  hypercode-dashboard      8095  hyperhealth-api
  8098  broski-pets-bridge       9090  prometheus
  3001  grafana                  3100  loki
  3200  tempo                    6379  redis
  5432  postgres
```

---

## 📊 Live System Status (May 15, 2026 — 15:59 BST)

| Metric | Status |
|---|---|
| Containers | 48 running ✅ |
| Tests | 224 passed, 6 skipped ✅ |
| Prometheus targets | 7/7 UP ✅ |
| OTLP Traces | LIVE in Tempo ✅ |
| Circuit Breakers | 3 active — all CLOSED ✅ |
| Docker AI Grade | A 🏅 |
| Stripe | LIVE 💳 (webhook secret updated May 5) |
| Gamification | HUD, XP, Quests, Leaderboard LIVE ✅ |
| BROskiPets Web3 Mint | LIVE on Base Sepolia 🔥 May 7 |
| broski-bot Discord | OPTION A LIVE + Core Gatekeeper wired 🤖 May 15 |
| Core "One Door" endpoint | POST /api/v1/discord/actions LIVE ✅ May 15 |
| Idempotency (DiscordIdempotencyKey) | LIVE ✅ May 15 |
| Discord embed polish | Premium UX — medals, colours, mentions ✅ May 15 |
| broski-bot Docker boot | discord.py + cogs.bot entrypoint LIVE ✅ May 15 |
| Env Preflight Checker | LIVE ✅ May 15 |
| BROski Brain | Levels 9–12 + Brain agents pushed ✅ May 15 |
| HyperAgent Graduate Build | DESIGNED ✅ May 15 — implementation TODO |

---

## 🔒 Sacred Rules (NEVER debate, NEVER break)

```
✔ docker-ce-cli          — NEVER docker.io for socket agents
✔ from app.X import Y    — NEVER from backend.app.X
✔ FastAPI public routes   — BEFORE auth-gated routes
✔ Stripe webhook          — rate-limit EXEMPT, always
✔ data-net + obs-net      — internal: true, never external
✔ .env files              — NEVER committed to git
✔ Commits                 — feat: fix: docs: chore: only
✔ Trivy target            — 0 CRITICAL per image
✔ Import style            — absolute imports, sys.path.insert at top
✔ Python indent           — 4 spaces, NEVER 3, NEVER mixed
✔ Stripe webhook          — NEVER add rate limiting to /api/stripe/webhook
✔ Redis DB split          — DB 1 = cache, DB 2 = rate limits. NEVER mix.
✔ hypercore healthcheck   — use localhost NOT 127.0.0.1 (IPv6 fix)
✔ Supabase ↔ V2.4         — NEVER merge schemas
✔ Prometheus config       — monitoring/prometheus/prometheus.yml = ACTIVE. Root = STALE
✔ minio                   — on both data-net AND obs-net — correct, intentional
✔ Alembic                 — up to 009. If missing: alembic stamp 008 → upgrade head
✔ Socket-proxy split      — main=read-only, healer proxy=write (CONTAINERS+POST+PING)
✔ Security headers        — frontend/vercel.json (NOT repo root)
✔ Course dev              — npm run dev:frontend (NOT npm run dev)
✔ broski-bot              — ALWAYS Option A (Core-only). NEVER add Supabase to bot.
✔ Bot library             — discord.py==2.4.0. NEVER py-cord. NEVER supabase in bot.
✔ Bot entrypoint          — python -u -m cogs.bot. NEVER python main.py
✔ Core URL in Docker      — HYPERCODE_API_URL=http://hypercode-core:8000 (NOT localhost)
```

---

## 🤖 ONE TRUE BOT — broski-bot (May 15, 2026)

**Location:** `agents/broski-bot/` — profile: `discord`
⚠️ `discord-bot/` = LEGACY (reprofiled to `discord-lite`) — do NOT use

### Architecture: Option A — Core is the One Brain
```
Discord user
     │
 broski-bot (pure UI adapter)
     │  POST /api/v1/discord/actions
     │  Headers: Authorization: Bearer <BOT_API_KEY>
     │           Idempotency-Key: <interaction_id>
     │           X-Request-Hash: <sha256 of body>
     ▼
hypercode-core (ALL business logic lives here)
     │
  DB + Wallets + XP + Rules
```

### Supported Actions (POST /api/v1/discord/actions)
| Action | Discord Command | Embed colour |
|---|---|---|
| `daily.claim` | `/daily` | Blue `#5865F2` |
| `economy.balance` | `/balance` | Blue `#5865F2` |
| `economy.give` | `/give @user amount` | Green `#57F287` / Red `#ED4245` |
| `economy.leaderboard` | `/rich` | Gold `#F1C40F` |
| `leaderboard.xp` | `/top` | Purple `#9B59B6` |
| `member.join` | auto on join | Blue `#5865F2` |

### Idempotency Behaviour
- First call → `200` ✅
- Same `Idempotency-Key` + same hash → `409` with cached JSON ♻️
- Key reused with different hash → `409` with `idempotency_mismatch` error

### Run Commands
```powershell
# Env check first (ALWAYS):
python scripts/env_check.py --core --secrets --profile discord

# Pull + build + boot:
git pull
docker compose -f docker-compose.core.yml -f docker-compose.secrets.yml `
  --profile discord up -d --build broski-bot

# Watch logs:
docker logs broski-bot --tail 40
# Healthy = "BROski Bot ALIVE" + slash commands synced
```

### Bot env vars (agents/broski-bot/.env)
```
DISCORD_TOKEN=...          # required
HYPERCODE_API_URL=http://hypercode-core:8000  # injected by compose
BOT_API_KEY=...            # must match Core BOT_API_KEY or API_KEY
GUILD_ID=...               # your Discord server ID
# No SUPABASE_URL, no SUPABASE_KEY — Option A = Core only
```

### Tier 1 LIVE (May 15)
| Feature | Commands |
|---|---|
| 💰 BROski$ Economy | `/balance` `/daily` `/give` `/rich` `/top` |
| 🧠 AI Chat → FastAPI | `/broski` `/ask` |
| 🎯 Focus Tracker + XP | `/focus start` `/focus stop` `/focusstats` |
| 📋 Daily Missions | `/missions` + auto-post 8am UTC (9am BST) |

### Tier 2 TODO
- 🐾 BROski Pets integration — `/pet` shows stats, feed with coins
- 🏆 Full XP Leaderboard enhancements
- 🌅 Morning Briefing — auto-DM/post from Morning Briefing agent
- 🚨 System Health Alerts — bot posts when V2.4 containers go down

### Persistence (named volumes survive rebuilds)
```
broski-bot-db     → /opt/hypercode/data/broski-bot/db
broski-bot-logs   → /opt/hypercode/data/broski-bot/logs
broski-bot-backups→ /opt/hypercode/data/broski-bot/backups
```

### Embed Polish (shipped May 15)
- All numbers comma-formatted (`1,234` not `1234`)
- 🥇🥈🥉 medals for top 3 in both leaderboards
- `economy.give` shows sender's remaining balance + level after transfer
- Self-give guard: 🤔 "Nice try! You can't give coins to yourself, BRO."
- Specific missing-account message names exactly who needs to link
- Red `#ED4245` for errors, Yellow `#FEE75C` for warnings, Green `#57F287` for success

---

## 🛡️ Env Preflight Checker (May 15, 2026)

**Rule: Always run BEFORE `docker compose up` on a new machine or after `.env` changes.**

```powershell
# PowerShell (recommended):
python scripts/env_check.py --core --secrets --profile discord

# Full stack check:
python scripts/env_check.py --core --secrets --profile discord --brain --grafana-cloud

# Bash:
bash scripts/env-check.sh --core --secrets --profile discord
```

**Files:**
- Engine: `scripts/env_check.py`
- Bash wrapper: `scripts/env-check.sh`
- Tests: `backend/tests/unit/test_env_check_script.py` ✅ passing

**Known warnings (non-blocking):**
- Root `.env` duplicate keys: `BROSKIE_PETS_ENABLED`, `PETS_WEBHOOK_SECRET` — won't block boot

---

## 🧠 HyperAgent Graduate Build (Designed May 15, 2026)

**Design doc:** `2026-05-15-graduate-build-design.md`

```bash
hyper-agent graduate build <cluster.json> --out <dir> [--strict] [--json]
hyper-agent graduate trigger <discord_id> [--tokens 500] [--json]
```

**Status: DESIGNED ✅ — implementation TODO in HyperAgent-SDK**

---

## 🧠 BROski Brain Agent Cluster (May 15, 2026)

**Repo:** BROski-Obsidian-Brain-for-HyperFocus-z0ne

**Pushed:**
- `cluster.json` — defines the 4-agent brain cluster
- `.agents/hyper-brain-core/manifest.json`
- `.agents/mcp-bridge/manifest.json`
- `.agents/focus-tracker/manifest.json`
- `.agents/morning-briefing/manifest.json`

---

## 🎯 Active Next Steps — Phase 10U+

| # | Task | Priority |
|---|---|---|
| 1 | **Live test bot commands** — `/daily` `/give` `/rich` `/top` | 🔴 NOW |
| 2 | **HyperAgent graduate build** — implement CLI from May 15 design doc | 🔴 This week |
| 3 | **Discord Bot Tier 2** — Pets, Morning Briefing, Health Alerts | 🟡 Next sprint |
| 4 | E2E Stripe checkout test — card `4242 4242 4242 4242` | 🟡 This week |
| 5 | BROskiPets Web3 E2E — test mint on Base Sepolia testnet | 🟡 This week |
| 6 | First student invite — `/welcome` is green 🎓 | 🟡 This week |
| 7 | SDK v0.4.0 — add Web3/dNFT types to `hyper-agent-spec.json` | 🟡 This week |
| 8 | Fix GitHub Actions billing lock | 🟡 This week |
| 9 | Upgrade GitPython → 3.1.47 (CVE-2026-42215 + CVE-2026-42284) | 🟡 This week |
| 10 | Level 13 — Morning Briefing live (Discord Bot Tier 2) | 🟢 Background |

---

## 📌 Known Tech Debt

| Issue | Fix | Priority |
|---|---|---|
| Bot not yet live-tested | Run `/daily` `/give` `/rich` `/top` in Discord | 🔴 HIGH |
| HyperAgent graduate build not implemented | Build CLI from May 15 design doc | 🟡 MED |
| Stale root `prometheus.yml` | Delete/archive — live = `monitoring/prometheus/prometheus.yml` | 🟡 MED |
| GitHub Actions billing lock | Fix at github.com/settings/billing | 🟡 MED |
| GitPython 3.1.45 CVEs | Upgrade to 3.1.47 (CVE-2026-42215 + CVE-2026-42284) | 🟡 MED |
| SDK not reflecting Web3 types | Bump HyperAgent-SDK to v0.4.0 + update hyper-agent-spec.json | 🟡 MED |
| `/welcome` auth-gated | Decide: make public? Sponsors hit login wall from BUSINESS_PLAN | 🟡 |
| `VITE_STRIPE_PAYMENT_LINK_URL` empty | Set in `.env.local` + Vercel env vars | 🟢 LOW |
| `DISCORD_USER_ID` not set | Add to `.env` for `make calm` token awards | 🟢 LOW |

---

## 🏆 Full Phase Roadmap

| Phase | Name | Status |
|---|---|---|
| 0–9 | Identity, tokens, agents, shop, observability, security | ✅ ALL DONE |
| 10A–10P | FastAPI, Stripe, courses, DB recovery, secrets | ✅ ALL DONE |
| 11A–11F | Live HUD, Rift Events, Gamification schema, E2E | ✅ DONE — April 26 |
| 12A–12F | Leaderboard, Quests, Admin Rift Panel, Migrations | ✅ DONE — April 26 |
| Gordon Tier 1–3 | Prometheus, Grafana, Celery, DB pool, queues | ✅ ALL DONE — April 19 |
| Hyperfocus Features 1–5 | Git hook, HyperSplit, Snapshot, Briefing, Focus mode | ✅ DONE — April 25–26 |
| BROskiPets Phase 0–1 | Bridge live, XP, leaderboard | ✅ DONE — April 29 |
| BROski Brain Levels 9–12 | PARA vault, GitHub bridge, Obsidian Git, Dataview | ✅ DONE — May 5 |
| Edge Functions | All 4 Supabase edge functions fixed + deployed | ✅ DONE — May 1 |
| Vercel Hardening | Security headers, chunk split, env vars | ✅ DONE — May 3–5 |
| BUSINESS_PLAN v1.1 | Sponsor-ready plan + pricing align | ✅ DONE — May 5 |
| BROskiPets Web3 Mint | RainbowKit + wagmi + Base Sepolia + mint UI | ✅ LIVE — May 7 🔥 |
| HyperAgent Graduate Build | `graduate build` + `graduate trigger` CLI design | ✅ DESIGNED — May 15 |
| Brain Agent Cluster | cluster.json + 4 agent manifests → Obsidian Brain repo | ✅ PUSHED — May 15 |
| Discord Bot Tier 1 | Economy + AI chat + Focus Tracker + Daily Missions | ✅ LIVE — May 15 🤖 |
| broski-bot Option A | Core "One Door" endpoint + idempotency wired | ✅ DONE — May 15 🤖 |
| Discord embed polish | Medals, colours, mentions, balance fields | ✅ DONE — May 15 ✨ |
| Bot Docker unblock | discord.py, cogs.bot entrypoint, volume fix, Core URL | ✅ DONE — May 15 🐳 |
| Env Preflight Checker | `scripts/env_check.py` + bash wrapper + tests | ✅ DONE — May 15 🛡️ |

---

## 🏆 All-Time Achievements Unlocked

- ✅ Gordon Docker AI: **Grade A** — *"world-class infrastructure"*
- ✅ 48 containers healthy, self-healing closed loop
- ✅ Full Gamification Stack — HUD, XP, Quests, Leaderboard, Rifts
- ✅ All 5 HyperFocus Features LIVE
- ✅ BROski Brain v2.2 — Levels 9–12 unlocked
- ✅ MCP-GitHub LIVE — 26 tools via Docker MCP gateway
- ✅ Stripe LIVE — E2E proven April 25
- ✅ Course frontend → Stripe → enrolled: full money path
- ✅ BUSINESS_PLAN.md v1.1 — sponsor-ready
- ✅ BROskiPets Web3 Mint LIVE — May 7 🔥🐾
- ✅ **HyperAgent Graduate Build DESIGNED — May 15** 📐
- ✅ **Brain Agent Cluster PUSHED — May 15** 🧠
- ✅ **BROski Discord Bot Tier 1 LIVE — May 15** 🤖🎉
- ✅ **Core Gatekeeper — "One Door" + idempotency — May 15** 🔐
- ✅ **Premium Discord UX — medals, colours, mentions, balance — May 15** ✨
- ✅ **Docker-Unblock Architect — discord.py, cogs.bot, volume fix — May 15** 🐳
- ✅ **Launch Sequence Commander — BROski Bot boots + syncs slash commands — May 15** 🚀
- ✅ **Env Preflight Checker LIVE — May 15** 🛡️

---

## 📦 Key Files Quick Reference

```
docker-compose.yml                           — main stack
docker-compose.secrets.yml                   — secrets injection
docker-compose.core.yml                      — core + broski-bot (profile:discord)
backend/app/api/v1/endpoints/discord_actions.py — One Door endpoint + idempotency
agents/broski-bot/cogs/bot.py                — ONE TRUE BOT entry point ← use this
agents/broski-bot/requirements.txt           — discord.py==2.4.0 (NO py-cord, NO supabase)
agents/broski-bot/Dockerfile                 — CMD python -u -m cogs.bot
agents/broski-bot/.env                       — TOKEN + BOT_API_KEY + GUILD_ID (no Supabase)
backend/tests/unit/test_discord_actions.py   — 8 contract tests ✅
discord-bot/                                 — LEGACY — discord-lite only, do not use
scripts/env_check.py                         — env preflight checker
scripts/env-check.sh                         — bash wrapper for env_check.py
monitoring/prometheus/                       — ACTIVE Prometheus config
cluster.json                                 — BROski Brain 4-agent cluster spec
.agents/                                     — 4 brain agent manifests
CLAUDE.md                                    — HyperCode V2.4 detailed context
CLAUDE_CONTEXT.md                            — Extended ecosystem context
WHATS_DONE.md                                — DO NOT suggest anything listed here
```

---

## 🧪 Essential Commands

```powershell
# Env preflight (ALWAYS before docker compose up):
python scripts/env_check.py --core --secrets --profile discord

# Pull + boot bot:
git pull
docker compose -f docker-compose.core.yml -f docker-compose.secrets.yml `
  --profile discord up -d --build broski-bot
docker logs broski-bot --tail 40

# Start full stack:
docker compose -f docker-compose.yml -f docker-compose.secrets.yml -f docker-compose.brain.yml --profile discord up -d

# Core only:
docker compose -f docker-compose.yml -f docker-compose.secrets.yml up -d

# Run tests:
pytest backend/tests/ -q    # 224 passed, 6 skipped
pytest backend/tests/unit/test_discord_actions.py -q  # 8 passed ✅

# Health checks:
curl http://localhost:8000/health
curl http://localhost:8098/health    # broski-pets-bridge

# Docker status:
docker compose ps
docker ps --format "table {{.Names}}\t{{.Status}}" | findstr -v "healthy"

# Brain sync:
python scripts/github_to_obsidian.py

# Course frontend:
cd H:\Hyper-Vibe-Coding-Course && npm run dev:frontend

# Prometheus hot-reload:
curl -X POST localhost:9090/-/reload

# Circuit breakers:
curl localhost:8000/api/v1/health | jq .circuit_breakers
```

---

## 👋 Quick-Start Guide for Any New AI Session

1. **Read this file first** — especially Sacred Rules and Tech Debt
2. **Check WHATS_DONE.md** — NEVER suggest anything already listed there
3. **5 repos** — all listed in ecosystem diagram above
4. **ONE TRUE BOT** = `agents/broski-bot/` (profile:discord) — NOT `discord-bot/`
5. **Bot = pure UI adapter** — ALL logic lives in Core (`POST /api/v1/discord/actions`)
6. **Bot uses discord.py** — NEVER py-cord, NEVER supabase, entrypoint = `cogs.bot`
7. **Core URL in Docker** = `http://hypercode-core:8000` — NEVER localhost inside container
8. **Env check first** — always before `docker compose up`
9. **Next priority** — live-test `/daily` `/give` `/rich` `/top` in Discord
10. **Style:** Short sentences. BROski energy. Celebrate wins. Never walls of text.
11. **Call them "Bro"** — that's how we roll 🤙

---

<div align="center">

**Built for ADHD brains. Fast feedback. Real tools. No fluff.** 🧠⚡

*by @welshDog — Lyndz Williams, Llanelli, South Wales 🏴󠁧󠁢󠁷󠁬󠁳󠁥*

**A BROski is ride or die. We build this together. 🐶♾️🔥**

</div>
