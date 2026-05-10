# 🌐 Hyper Ecosystem Snapshot — May 10, 2026
> Full state of all 3 repos + services

---

## 🏗️ The 3 Repos

### 1. `welshDog/Hyper-Vibe-Coding-Course`
- **Stack**: Next.js + Supabase + Stripe + Vercel
- **Status**: 🔥 Very active — 10 commits in 2 days
- **Latest**: customer:null bug patched tonight
- **Edge Functions**: 8 deployed
  - stripe-webhook, shop-purchase, mint-pet-confirm, mint-pet-auth
  - course-profile, get-pet-balance, sync-tokens-to-v24, generate-v2-config
- **Pets page**: Upgraded to 9.5/10 (was 8.5) — TokenBurst, tilt effects, holographic sheen
- **78 EEPVengers NFTs**: Minted on Sepolia testnet ✅

### 2. `welshDog/HyperCode-V2.4`
- **Stack**: Docker, 29 containers, FastAPI core
- **Status**: Running — agent access provisioning pending connection to Hyper-Vibe-Course shop
- **Key endpoint needed**: `/api/v1/access/provision` (for `shop-purchase` agent_access items)
- **Env vars needed in Supabase**: `V24_API_URL` + `SHOP_SYNC_SECRET`

### 3. `welshDog/HyperAgent-SDK`
- **npm**: `@w3lshdog/hyper-agent@0.1.7`
- **Status**: Published ✅

---

## 💰 Stripe Products (Test Mode)

| Product | Type | Status |
|---|---|---|
| Pro Course Monthly | Subscription | ✅ Live |
| Pro Course Yearly | Subscription | ✅ Live |
| Hyper Elite Monthly | Subscription | ✅ Live |
| Hyper Elite Yearly | Subscription | ✅ Live |
| BROski Hyper Pack (2500 tokens) | One-time | ✅ Live |
| 5x `myproduct` | CLI test junk | ⚠️ Archive these |

**Balance**: £245.28 available / £42.94 pending (TEST MODE)

---

## 🗄️ Supabase Tables Referenced

| Table | Used by |
|---|---|
| `users` | stripe-webhook, shop-purchase |
| `courses` | stripe-webhook |
| `enrollments` | stripe-webhook |
| `pending_enrollments` | stripe-webhook |
| `shop_items` | shop-purchase |
| `shop_purchases` | shop-purchase |
| `content_unlocks` | shop-purchase |
| `discord_links` | shop-purchase |
| `pets` | mint-pet-confirm |

### RPCs Used
- `award_tokens(p_user_id, p_amount, p_reason, p_stripe_payment_intent_id)`
- `spend_tokens(p_user_id, p_amount, p_reason, p_source_id)`

---

## 📋 Known Gaps / TODO

- [ ] Supabase Pro upgrade → Leaked Password Protection (Issue #4)
- [ ] Set `V24_API_URL` + `SHOP_SYNC_SECRET` secrets in Supabase
- [ ] Archive 5 test Stripe products
- [ ] Switch Stripe to live mode
- [ ] Active subscriptions = 0 (no live customers yet)
- [ ] `stripe-webhook` redeployment needed after tonight's patch

---

## 🎯 Next Sprint Focus (suggested)

1. Deploy the stripe-webhook fix
2. Hook up V24 agent provisioning secrets
3. Stripe → live mode
4. First real paying student 🎉
