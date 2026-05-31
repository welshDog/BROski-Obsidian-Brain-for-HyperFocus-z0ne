---
type: area
title: Admin Radar
tags:
  - area
  - admin
  - bills
  - domains
created: 2026-05-31
updated: 2026-05-31
---

# 📋 Admin Radar

> Everything "adulting" in one place. Check monthly. Don't let renewals sneak up.

---

## 💳 Subscriptions & Renewals

| Service | Cost | Renewal | Status | Notes |
|---|---|---|---|---|
| Vercel (bro-skis team) | Free / Pro? | — | ✅ Active | Course + Showcase hosted |
| Supabase | Free tier | — | ✅ Active | Course DB + Auth |
| GitHub Pro | — | — | — | All repos |
| Domain(s) | — | — | — | Check expiry dates! |
| Stripe | Pay-as-you-go | — | ✅ Active | Test mode mostly |
| Docker Hub | Free | — | ✅ | Container images |

> 📌 Full list: [[03-Resources/Subscriptions-and-Wishlist]]

---

## 🔑 Secrets & Credentials Checklist

- [ ] GitHub PAT — still valid? (check expiry)
- [ ] Stripe API keys — test vs live mode correct?
- [ ] Supabase service role key — rotated recently?
- [ ] Vercel env vars — synced with `.env.local`?
- [ ] Docker registry — login still works?

> ⚠️ **Never put actual secrets in Obsidian.** This is a CHECKLIST, not a password manager.

---

## 📦 Hardware / Local Infra

| Thing | Status | Notes |
|---|---|---|
| Main PC | — | Windows, HperCore workspace |
| RAM | 16–32GB | 32 containers need it |
| Storage | — | Check free space monthly |
| Backups | — | Obsidian Git auto-push ON |

---

## 📅 Monthly Admin Ritual

- [ ] Check all subscription renewal dates
- [ ] Verify GitHub PAT hasn't expired
- [ ] Review Stripe dashboard for any failed payments
- [ ] Check domain expiry dates
- [ ] Review Docker disk usage (`docker system df`)
- [ ] Archive completed projects → `04-Archive/`
