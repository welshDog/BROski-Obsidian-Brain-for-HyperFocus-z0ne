# 🏥 Ecosystem Health Report — May 10, 2026
> Session dump by Perplexity AI + Lyndz Williams
> Time: 8:17 PM BST

---

## 🐙 GitHub — `welshDog/Hyper-Vibe-Coding-Course`

| Check | Status |
|---|---|
| Open PRs | ✅ 0 — clean |
| Open Issues | ⚠️ 1 (wishlist, not a blocker) |
| Latest commit | ✅ `7c01b0d` — customer:null fix |
| Recent activity | 🔥 10 commits in 2 days |
| Branch conflicts | ✅ None |

### Recent Commits (May 8–10)
- `7c01b0d` — fix: resolve customer:null crash — use payment_intent string safely
- `5a1729d` — docs: Live Verification Addendum v2 - Gordon health check corrections
- `8199c63` — docs: update ULTIMATE_AUDIT_REPORT to v2.0
- `3bdc689` — docs: design-brain elevation + EEPVengers mint
- `ef03137` — fix: respect reduce-motion preference in UI animations
- `fb63157` — feat(pets): BROski$ celebration + TokenBurst particles
- `c1288dc` — feat(mint): wallet-signed mint persistence + confirm endpoint

### Open Issues
- `#4` 🔒 Supabase Leaked Password Protection — needs Pro plan (~£25/mo). Not urgent.

---

## 🗄️ Supabase Edge Functions

| Function | Status |
|---|---|
| `stripe-webhook` | ✅ Patched tonight (customer:null fix) |
| `shop-purchase` | ✅ Full — spend tokens, bonus content, V2.4 agent provisioning |
| `mint-pet-confirm` | ✅ Wallet-signed mint persistence |
| `mint-pet-auth` | ✅ Present |
| `course-profile` | ✅ Present |
| `get-pet-balance` | ✅ Present |
| `sync-tokens-to-v24` | ✅ Present |
| `generate-v2-config` | ✅ Present |

### ⚠️ Watch: `shop-purchase` agent provisioning
`V24_API_URL` + `SHOP_SYNC_SECRET` env vars needed.
If not set → agent_access items queue as `pending` (not a crash, just a stub).

---

## 💳 Stripe

| Check | Status |
|---|---|
| Mode | ⚠️ TEST MODE (`livemode: false`) |
| Disputes | ✅ 0 — clean |
| Active subscriptions | ⚠️ 0 — none live yet |
| Customers | ✅ 1 test customer |
| Recent payments | ✅ 5 succeeded |

### Balance
- 💰 Available: **£245.28 GBP**
- ⏳ Pending: **£42.94 GBP**

### Products Live
- ✅ Pro Course Monthly
- ✅ Pro Course Yearly
- ✅ Hyper Elite Monthly
- ✅ Hyper Elite Yearly
- ✅ BROski Hyper Pack (2500 tokens)
- ⚠️ 5x `myproduct` CLI test junk — safe to archive/delete

### Payment Intents
All 5 recent: `succeeded` but had `customer: null` → **root cause of tonight's bug. Now fixed.**

---

## 🎯 Priority Action List

| Priority | Action |
|---|---|
| 🔴 Do first | `supabase functions deploy stripe-webhook --no-verify-jwt` |
| 🟡 Soon | Set `V24_API_URL` + `SHOP_SYNC_SECRET` in Supabase secrets |
| 🟡 Soon | Delete/archive 5 test `myproduct` Stripe products |
| 🟠 When funded | Upgrade Supabase Pro → enable Leaked Password Protection |
| 🟢 Nice to have | Switch Stripe to live mode when ready for real payments |
