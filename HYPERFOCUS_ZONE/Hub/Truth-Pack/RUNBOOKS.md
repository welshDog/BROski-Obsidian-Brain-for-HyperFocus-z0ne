# 🛠️ RUNBOOKS.md — How To Do Things
> Step-by-step. Verified. Never guess — check here first.
> Updated: 2026-05-28

---

## 🚀 Start the Full Stack
```bash
# Main stack + secrets
docker compose -f docker-compose.yml -f docker-compose.secrets.yml up -d

# AI agents
docker compose --profile ai up -d

# Discord bot
docker compose --profile discord up -d broski-bot

# NemoClaw agent
docker compose --profile nemoclaw up -d

# Course frontend (NOT npm run dev — that breaks AI agents)
cd H:\Hyper-Vibe-Coding-Course && npm run dev:frontend

# Full ops server (course + server together)
npm run dev:full
```

---

## 🧪 Run Tests
```bash
# HyperCode backend (251 pass, 6 skip expected)
pytest backend/tests -q

# HyperAgent-SDK
cd H:\HyperAgent-SDK && npm test
# Expected: 72 passed, 0 failed

# Course Playwright E2E
cd H:\Hyper-Vibe-Coding-Course && npx playwright test
# Expected: 99/99 green (chromium + firefox + webkit)

# BROskiPets Foundry
cd contracts && forge test --match-contract BROskiPet -v
# Expected: 22/22 pass
```

---

## 🗄️ Apply a DB Migration (Supabase)
```bash
# NEVER: supabase db push
# ALWAYS: apply_migration via Supabase MCP or dashboard
# Command format:
supabase migration new <migration_name>
# Then apply via MCP apply_migration tool
```

---

## 🔥 Focus Mode
```bash
make focus   # stops 14 non-essential containers + starts 25-min timer
make calm    # restores all containers + awards 75 BROski$
```

---

## 🤖 GitHub → Obsidian Sync
```bash
# Run manually (needs GITHUB_PAT in env)
python scripts/github_to_obsidian.py

# Auto-sync: Obsidian Git commits vault every 10 mins automatically
```

---

## 🐾 Deploy BROskiPets Contract (BLOCKED — wallet funding needed)
```bash
# Unblock: generate fresh wallets, fund from Trust Wallet Send
cast wallet new  # get fresh deployer key

# Then deploy:
forge script script/DeployBROskiPet.s.sol \
  --rpc-url https://sepolia.base.org \
  --private-key $DEPLOYER_KEY \
  --broadcast --verify \
  --etherscan-api-key $ETHERSCAN_API_KEY \
  --root H:/dNFTpet/BROskiPets-LLM-dNFT/contracts
```

---

## 📦 Publish HyperAgent-SDK to npm
```bash
cd H:\HyperAgent-SDK
npm version patch  # or minor/major
npm publish --access public
# Registry target: @w3lshdog/hyper-agent
# Current: npm=0.1.7, code=0.4.0
```

---

## 🔐 Rotate/Add Secrets
- Stripe keys: Supabase Edge Function env vars (dashboard)
- Discord bot token: `.env` only — NEVER commit
- Docker secrets: `secrets/` folder as `.txt` files (gitignored)
- Vercel env vars: Vercel dashboard → BROskis team → project settings

---

## 🩺 Health Checks
```bash
curl http://127.0.0.1:8088              # Dashboard
curl http://localhost:8099/health       # NemoClaw
curl http://localhost:8098/health       # broski-pets
curl http://localhost:8088/api/health   # Core
curl https://hyper-agents-ide.onrender.com/api/health  # Render IDE
```

---

## 🧠 Session Handover Protocol
1. Read `HYPERFOCUS_ZONE/Hub/Truth-Pack/SYSTEM_STATUS.md` first
2. Read repo-specific `NEXT_SESSION_HANDOVER_[date].md`
3. Check `WHATS_DONE.md` before building anything
4. State the next task in 2 lines
5. Push to GitHub after every task — nothing is done until committed
