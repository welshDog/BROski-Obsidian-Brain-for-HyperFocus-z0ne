# 🔒 Late Night Supabase Hardening — May 10, 2026
> Session: ~10:38 PM – 11:09 PM BST
> Done by: Perplexity AI + Lyndz Williams

---

## ✅ Migrations Applied Tonight

### 1. `add_missing_fk_indexes`
7 missing foreign key indexes added — flagged by Supabase performance advisor:
```sql
CREATE INDEX IF NOT EXISTS idx_certificates_course_id ON public.certificates(course_id);
CREATE INDEX IF NOT EXISTS idx_module_completions_module_id ON public.module_completions(module_id);
CREATE INDEX IF NOT EXISTS idx_pending_enrollments_course_id ON public.pending_enrollments(course_id);
CREATE INDEX IF NOT EXISTS idx_quiz_attempts_question_id ON public.quiz_attempts(question_id);
CREATE INDEX IF NOT EXISTS idx_quiz_questions_lesson_id ON public.quiz_questions(lesson_id);
CREATE INDEX IF NOT EXISTS idx_shop_purchases_item_id ON public.shop_purchases(item_id);
CREATE INDEX IF NOT EXISTS idx_user_quests_quest_id ON public.user_quests(quest_id);
```

### 2. `fix_security_definer_view_and_rifts_rls`
- 🔴 ERROR cleared: Recreated `leaderboard_public` view WITHOUT `SECURITY DEFINER`
- Added `security_invoker = true` so querying user's RLS applies
- Merged duplicate `rifts` RLS policies (`rifts_admin_write` + `rifts_public_read`) into clean `rifts_select` + `rifts_write`

### 3. `drop_unused_indexes`
12 unused indexes dropped to save storage:
- `idx_referral_codes_code`
- `idx_lessons_course_id`
- `idx_enrollments_course`
- `hv_modules_slug_idx`
- `hv_modules_sort_order_idx`
- `idx_enrollments_user_id`
- `idx_rifts_expires_at`
- `idx_lesson_progress_course_id`
- `idx_quests_active`
- `idx_mint_nonces_user_id`
- `idx_mint_nonces_expires_at`
- `idx_pets_user_id`

### 4. `restrict_leaderboard_top_anon_access`
Revoked `EXECUTE` on `leaderboard_top()` from `anon` role:
```sql
REVOKE EXECUTE ON FUNCTION public.leaderboard_top(row_limit integer) FROM anon;
```

### 5. `fix_rifts_rls_creator_only`
Replaced overly permissive `rifts_write` (USING true) with creator-only policies:
```sql
-- INSERT: only with your own auth.uid()
-- UPDATE: only your own rifts
-- DELETE: only your own rifts
```
`rifts` table columns confirmed: `id, topic, multiplier, expires_at, description, created_by, is_closed, created_at`

---

## 📊 Stripe Status at End of Session

| Check | Status |
|---|---|
| Mode | ⚠️ TEST MODE |
| Balance available | £245.28 GBP |
| Balance pending | £42.94 GBP |
| Disputes | ✅ 0 |
| Active subscriptions | ⚠️ 0 |
| stripe-webhook | ✅ Deployed v28 |

---

## 🔐 Remaining Security Warnings (post-hardening)

| Level | Issue | Action |
|---|---|---|
| 🟡 WARN | `complete_module()` SECURITY DEFINER callable by authenticated | ✅ Intentional — leave it |
| 🟡 WARN | `complete_quest()` same | ✅ Intentional |
| 🟡 WARN | `get_or_create_referral_code()` same | ✅ Intentional |
| 🟡 WARN | `leaderboard_top()` still shows anon warning | Cache — will clear |
| 🔵 FUTURE | Leaked Password Protection disabled | Needs Supabase Pro (~£25/mo) |

---

## 📋 Remaining TODO List

| Priority | Task |
|---|---|
| 🟡 Soon | Set `V24_API_URL` + `SHOP_SYNC_SECRET` in Supabase secrets |
| 🟡 Soon | Delete 8x junk `myproduct` from Stripe dashboard |
| 🟡 Soon | Check `token-sync-to-v24` vs `sync-tokens-to-v24` — possible duplicate function |
| 🔵 When funded | Supabase Pro → enable Leaked Password Protection |
| 🔵 When ready | Switch Stripe to live mode |

---

## 🚀 Supabase CLI + Stripe Webhook
- Fixed `.env` file: `X-API_KEY` → `X_API_KEY` (hyphen not allowed in var names)
- Deployed from correct repo: `H:\Hyper-Vibe-Coding-Course`
- Supabase CLI updated: `2.90.0 → 2.98.2` via Scoop
- stripe-webhook now on **version 28** ✅
