---
project: true
status: Active
coins: 0
xp: 0
tags: [project, course, stripe, supabase, web3, pets]
updated: 2026-05-27
---

# 🎓 Hyper-Vibe Coding Course

## Why Matters
This is the revenue engine for HYPERFOCUS Z0ne: course platform + Stripe + Supabase auth + lesson gating + BROski$ token rewards. Web3 BROskiPets exists but monetization comes first.

## Current Status (May 27, 2026)
- ✅ Frontend live on Vercel: https://hyper-vibe-coding-course.vercel.app
- ✅ Supabase project: `yhtmuibgdnxhbgboajhc`
- ✅ Stripe tier map updated to 5 tiers (8 live price IDs total)
- ✅ `stripe-webhook` deployed (CURRENT: v39) with idempotency + refund/dispute handling
- ✅ DB schema verified: `users.subscription_tier` accepts `free|pro|hyper|starter|builder|hyper_legend`
- ✅ `enrollments` table ready (`status` + `user_email` now written by webhook for debugging)

## 🔴 Blockers (NOW)
- 🔴 Revenue switch proof not executed yet: **£1 smoke test** to confirm rows in `enrollments` + `token_transactions`

## Next 3 Moves
- [ ] **£1 smoke test** (buy a tier) → confirm `enrollments` + `token_transactions`
- [ ] Refund test → confirm `enrollments.status` becomes `revoked`
- [ ] After revenue proof: wire Mission Control items (CatchStragglers + `mc_events` usage) without touching Sprint 4

## 🧪 Smoke Test SQL (after £1 purchase)
```sql
select * from enrollments order by created_at desc limit 5;
select * from token_transactions order by created_at desc limit 10;
```

## Refund Verification SQL
```sql
select status from enrollments where user_id = '<your-user-id>';
```

## ⚠️ Open Decisions
- Make `/welcome` public? Sponsors clicking from BUSINESS_PLAN hit `/login`
- V2.4 sync endpoint for `pets` / `mint_nonces`? Or pure Supabase?
- Phase 2A.5 architecture: on-chain event listener vs frontend POST + receipt verify

## Web3 / Pets (Backlog Until Revenue Switch)
- [ ] Set `VITE_MINT_VIA_RELAY=true` on Vercel (all envs)
- [ ] Fund relayer wallet with Base ETH
- [ ] E2E mint test on Base Sepolia → confirm row in `pets` table

## Links
- [Repo](https://github.com/welshDog/Hyper-Vibe-Coding-Course)
- Session handover: `H:\HYPERFOCUSZONE\HperCore\Hyper-Vibe-Coding-Course\NEXT_SESSION_HANDOVER_2026-05-27.md`
- Platform status report: `H:\HYPERFOCUSZONE\HperCore\Hyper-Vibe-Coding-Course\rewrites\PLATFORM_STATUS_REPORT_2026-05-27.md`
- [[BROskiPets]]
- [[HyperCode-V2.4]]
