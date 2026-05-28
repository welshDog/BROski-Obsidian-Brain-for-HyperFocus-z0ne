# 🧠 DECISIONS.md — Why We Did Things
> Rationale log. Before reversing a decision, read why it was made.
> Updated: 2026-05-28

---

## Architecture Decisions

### ✅ One Door — Discord Bot calls Core only (not Supabase direct)
- **Date:** 2026-05-15
- **Why:** Keeps all business logic in one place. Bot is a dumb relay — Core is the brain. Prevents data drift.
- **Rule:** `broski-bot` → `POST /api/v1/discord/actions` ONLY. No Supabase SDK in bot.

### ✅ GitPython pinned to 3.1.50 (not 3.1.47)
- **Date:** 2026-05-22
- **Why:** All docs said 3.1.47 but Trivy shows 5 advisories open on 3.1.45 and 3.1.47 only clears 2. 3.1.50 clears all 5 including an RCE (`GHSA-mv93-w799-cj2w`).
- **Proof:** Trivy scan on `hypercode-core` container. Commit `2d11313`.

### ✅ Vite + React (NOT Next.js) for Hyper-Vibe-Coding-Course
- **Date:** Established early 2026
- **Why:** Next.js App Router adds complexity we don't need. Vite is faster to iterate. Vercel deploys both fine.
- **Rule:** Never generate Next.js / App Router patterns for this repo.

### ✅ Web3 scoped to `/pets` route only
- **Date:** 2026-05-07
- **Why:** RainbowKit + wagmi context must NOT leak into global app root — breaks non-Web3 pages.
- **Rule:** Web3 providers stay inside the Pets page tree.

### ✅ `supabase db push` banned — use `apply_migration` only
- **Date:** Pre-May 2026
- **Why:** DB push desynced migrations once and caused a full audit. `apply_migration` is safe and tracked.

### ✅ Security functions changed to SECURITY INVOKER
- **Date:** 2026-05-16
- **Why:** `complete_module`, `complete_quest`, `get_or_create_referral_code` were SECURITY DEFINER — callable by anon role. Fixed to INVOKER so RLS applies properly.

### ✅ Truth Pack principle — Proof beats memory
- **Date:** 2026-05-28
- **Why:** 3 AI brains working on the same ecosystem kept contradicting each other. Any claim not backed by a link, query result, or log excerpt is not allowed in SYSTEM_STATUS.

### ✅ HyperAgent-SDK publish pending at v0.1.7 while code is v0.4.0
- **Date:** 2026-05-22
- **Why:** npm publish requires conscious decision — not auto-triggered. Don't publish until E2E checkout + BROskiPets deploy are validated.

---

## Token Economy Decisions

### ✅ BROski$ tiers: starter=200, builder=800, hyper=2500
- **Why:** Mirrors price tier value. Starter gets enough to try shop items; Hyper gets enough to mint a pet.

### ✅ Guardian P3c — ban ONLY on explicit ✅ APPROVE click
- **Why:** Autonomous bans are irreversible and legally risky. Human-in-the-loop is non-negotiable.
