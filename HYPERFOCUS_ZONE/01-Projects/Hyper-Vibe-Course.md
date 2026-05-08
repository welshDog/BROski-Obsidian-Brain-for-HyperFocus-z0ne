---
project: true
status: Active
coins: 0
xp: 0
tags: [project, course, stripe, supabase, web3, pets]
updated: 2026-05-08
---

# 🎓 Hyper-Vibe Coding Course

## Why Matters
Course platform. Stripe live. BROski$ token rewards for students. **Web3 BROskiPets mint live on `/pets`**. Sponsor-ready BUSINESS_PLAN.md.

## Current Status (May 8, 2026)
- ✅ Stripe checkout + payment-success live (May 5 fix)
- ✅ 7 courses seeded in Supabase
- ✅ BROski$ auto-award on purchase
- ✅ Vercel `VITE_*` env vars set on all 3 envs
- ✅ Supabase DB hardened (RLS init plan, FK indexes, perf fixes)
- ✅ Vercel security headers + LCP preload + WebP hero live
- ✅ Full gamification stack (HUD, XP, Rifts, Leaderboard, Quests) — April 26
- ✅ **BROskiPets Web3 Mint LIVE — May 7** (RainbowKit + Base + Edge Fn auth)
- ✅ **Phase 2A pet persistence — May 8** (Edge Fn v4 + `pets` table + `useMyPets` + `PetCard`)
- ✅ **Phase 2B Evolution Timeline — May 8 (this session)**
- ✅ **Phase 2C Squad row + How-XP-feeds-pet — May 8 (this session)**
- ✅ **Phase 2D Polish pass — May 8 (this session)** — skeletons, gold sweep, border-pulse, empty state, fade-in-up stagger

## 🔴 Blockers (NOW)
- 🔴 Set `VITE_MINT_VIA_RELAY=true` on Vercel (all 3 envs) — without it, mints succeed on-chain but NO `pets` row inserts
- 🔴 Fund relayer wallet with Base ETH (Sepolia + mainnet)
- 🔴 E2E mint test on Base Sepolia → confirm row in `pets` table → reload check

## Next 3 Moves
- [ ] Set `VITE_MINT_VIA_RELAY=true` on Vercel + redeploy
- [ ] Phase 2A.5 — `mint-pet-confirm` Edge Fn (wallet-signed mode persistence)
- [ ] Stripe live E2E (`stripe listen` + card 4242…)

## ⚠️ Open Decisions
- Make `/welcome` public? Sponsors clicking from BUSINESS_PLAN hit `/login`
- V2.4 sync endpoint for `pets` / `mint_nonces`? Or pure Supabase?
- Phase 2A.5 architecture: on-chain event listener vs frontend POST + receipt verify

## Links
- [Repo](https://github.com/welshDog/Hyper-Vibe-Coding-Course)
- Single source of truth: `H:\Hyper-Vibe-Coding-Course\CLAUDE.md`
- Sprint plan: `HYPER_ECOSYSTEM_PLAN_MAY4.md` Section B
- Phase 2 spec: `pets_page_deepdive_plan.md`
- [[BROskiPets]]
- [[HyperCode-V2.4]]
