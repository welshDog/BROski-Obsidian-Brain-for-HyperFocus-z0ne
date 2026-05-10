# 🔧 Stripe Webhook Fix — May 10, 2026
> Commit: `7c01b0d` on `welshDog/Hyper-Vibe-Coding-Course`
> File: `supabase/functions/stripe-webhook/index.ts`

---

## 🐛 The Bug

`customer: null` was crashing the `award_tokens` RPC call.

Stripe's `session.payment_intent` can be:
- A plain string ID (`"pi_3TV..."`) — normal
- An expanded `PaymentIntent` object — when Stripe expands it
- `null` — when no payment intent exists

The old code:
```ts
p_stripe_payment_intent_id: session.payment_intent as string ?? session.id,
```

❌ `as string` casts BEFORE `??` evaluates — so `null as string` = `null`, and `??` never fires.

---

## ✅ The Fix

```ts
// Safely resolve payment_intent to string before passing
const paymentIntentId =
  typeof session.payment_intent === 'string'
    ? session.payment_intent
    : (session.payment_intent as Stripe.PaymentIntent | null)?.id ?? session.id;

p_stripe_payment_intent_id: paymentIntentId,
```

### Why it works
- `typeof === 'string'` → use it directly ✅
- Object (expanded PaymentIntent) → grab `.id` ✅
- `null` → fall back to `session.id` ✅

---

## 🚀 Deploy Command

```bash
supabase functions deploy stripe-webhook --no-verify-jwt
```

> ⚠️ `--no-verify-jwt` is required — webhook calls come from Stripe, not logged-in users.

---

## 📋 Full Webhook Event Coverage

| Event | Handler | What it does |
|---|---|---|
| `checkout.session.completed` | `handleCheckoutCompleted` | Course enroll OR token pack award |
| `charge.refunded` | `handleChargeRefunded` | Deduct tokens for refunded token packs |

### Branch logic in `handleCheckoutCompleted`
- `metadata.token_amount` present → **Branch A**: award BROski$ tokens via `award_tokens` RPC
- No `token_amount` → **Branch B**: enroll in course via `enrollments` table
  - User registered → enroll immediately
  - User NOT registered → save to `pending_enrollments`, send Resend email

---

## 🔐 Security Model
- All logic runs AFTER `stripe.webhooks.constructEventAsync()` — Stripe-signed only
- `courseId` / `tokenAmount` come from Stripe metadata, never from the browser
- `userId` always resolved from Stripe-verified customer email
