# 🔴 KNOWN_ISSUES.md — Open Blockers
> Exact symptoms. Exact workarounds. No vague notes.
> Updated: 2026-05-28

---

## 🔴 BLOCKED — BROskiPets Contract Deploy
- **Symptom:** `forge deploy` fails — `DEPLOYER_KEY` unlocks a wallet with 0 ETH on Base Sepolia
- **Root cause:** Funded wallets (`0xBc548e...`, `0x2c2417...`) use Trust Wallet Extension which cannot export private keys
- **Workaround:** Run `cast wallet new` → get fresh deployer wallet → use Trust Wallet **Send** to transfer ~0.005 ETH from `0xBc548e...` to new address → update `.env`
- **Affected:** `BROskiPets-LLM-dNFT` repo, Path A relay testing, Pinata evolver agent (needs `BROSKIPET_CONTRACT_ADDRESS`)
- **Proof:** HANDOFF.md 2026-05-08 — wallet key/address mismatch documented

---

## ⚠️ HyperAgent-SDK npm out of sync
- **Symptom:** `npm install @w3lshdog/hyper-agent` installs v0.1.7 but code is v0.4.0
- **Impact:** External users get old version without Web3/dNFT manifest types
- **Fix:** `npm publish` — held until BROskiPets + E2E checkout validated
- **Proof:** Commit `7474f2a` (v0.4.0), npm registry confirmed 0.1.7

---

## 🔴 github-sync container — Unhealthy
- **Symptom:** Container health check failing
- **Fix:** Add `GITHUB_PAT=<your token>` to `.env` then `docker compose restart github-sync`
- **Impact:** Obsidian brain auto-sync from GitHub won't run

---

## 🔴 project-strategist container — Exited
- **Symptom:** Container exits immediately on start
- **Fix:** `docker exec project-strategist pip install perplexity-api`
- **Impact:** Perplexity-based strategy agent offline

---

## ⚠️ BACKEND_SIGNER_PRIVATE_KEY deleted from local .env
- **Symptom:** Local Path A BROskiPets relay testing fails
- **Impact:** Local only — cloud vaults (Pinata + Supabase Edge Functions) still have the key
- **Fix:** Generate new signer with `cast wallet new` or restore from cloud vault
- **Proof:** HANDOFF.md 2026-05-08

---

## ⚠️ Supabase migration 20260507080000 — Status Unconfirmed
- **Symptom:** `broskipet_mint_hardening.sql` was written but not confirmed applied
- **Impact:** Possible duplicate RLS policy on `mint_nonces` + `search_path` advisory warnings
- **Fix:** Check Supabase advisor dashboard → apply if not already done
- **Proof:** HANDOFF.md 2026-05-08 — "STATUS UNCONFIRMED"

---

## ⚠️ Render — Hyper-Agents-IDE on Free Tier (no disk persistence)
- **Symptom:** DB + exports reset on container restart
- **Impact:** Trained agent skills lost on redeploy
- **Fix:** Upgrade to Render Starter + add `/app/persist` disk mount
- **Env vars to update after upgrade:**
  - `TRAE_DB_PATH=/app/persist/data/trae.db`
  - `TRAE_EXPORTS_DIR=/app/persist/exports`
- **Proof:** NEXT_SESSION_HANDOVER_2026-05-26.md

---

## ⚠️ GitHub Actions — Billing Lock
- **Symptom:** Actions may be rate-limited or blocked
- **Fix:** github.com/settings/billing — check plan
- **Impact:** CI/CD pipelines may not run

---

## ℹ️ Sprint 4 — Claude's Work Unverified
- **Symptom:** `useAnonymousProgress.ts` + `migrateAnonProgress.ts` + `ClaimXPModal.tsx` shipped by Claude but not smoke-tested
- **Fix:** Manual verify — load `/vibe-labs/level-1`, check XP migration flow, check modal fires
- **Proof:** NEXT_SESSION_HANDOVER_2026-05-26.md (Course repo)
