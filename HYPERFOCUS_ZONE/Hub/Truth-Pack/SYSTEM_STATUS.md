# 🟢 SYSTEM_STATUS.md — Current Reality
> **Rule: Only facts with proof links allowed here. No memory, no guesses.**
> Updated: 2026-05-28 17:10 BST | Brain: Perplexity (Perplexity AI)

---

## 🔴 STATUS LEGEND
| Icon | Meaning |
|---|---|
| 🟢 | Live + verified |
| 🟡 | In progress / partial |
| 🔴 | Blocked |
| ⚠️ | Known issue — tracked in KNOWN_ISSUES.md |

---

## 🖥️ LIVE SYSTEMS

| System | Status | Last Verified | Proof Link |
|---|---|---|---|
| Vercel — Hyper Vibe Coding Course | 🟢 Live | 2026-05-22 | https://hyper-vibe-coding-course.vercel.app |
| Supabase — Hyper Vibe Course | 🟢 ACTIVE_HEALTHY | 2026-05-22 | Project: `yhtmuibgdnxhbgboajhc` |
| HyperCode-V2.4 Docker Stack | 🟢 48 containers healthy | 2026-05-22 | `docker ps` |
| broski-bot (Discord) | 🟢 Running | 2026-05-22 | Docker profile: discord |
| NemoClaw Agent | 🟢 L1-3.5 alive | 2026-05-22 | http://localhost:8099/health |
| Dashboard (hypercode-dashboard) | 🟢 5 tabs live | 2026-05-21 | http://127.0.0.1:8088 |
| Hyper-Agents-IDE | 🟢 Live on Render | 2026-05-26 | https://hyper-agents-ide.onrender.com/ |
| Stripe webhook (vibe-hook) | 🟢 Active | 2026-05-16 | 3 deliveries, 0 failures, avg 615ms |
| BROskiPets — Solidity contract | 🟡 22/22 tests pass | 2026-05-08 | NOT deployed — blocked on Base Sepolia wallet funding |
| github-sync container | 🔴 Unhealthy | 2026-05-21 | Needs GITHUB_PAT in .env |
| project-strategist container | 🔴 Exited | 2026-05-21 | Needs `pip install perplexity-api` |

---

## 📦 REPO + CODE STATE

| Repo | Latest Notable Commit | Status |
|---|---|---|
| HyperCode-V2.4 | GitPython pinned 3.1.50 (`2d11313`) + TRUTH.md + docs/TRUTH_PACK added | 🟢 |
| HyperAgent-SDK | v0.4.0 code done, npm still on 0.1.7 + TRUTH.md + docs/TRUTH_PACK added | ⚠️ publish pending |
| Hyper-Vibe-Coding-Course | 99/99 Playwright green, Sprint 4 in flight + TRUTH.md + docs/TRUTH_PACK added | 🟡 |
| BROskiPets-LLM-dNFT | Truth Pack v2.1 added — TRUTH.md + docs/TRUTH_PACK. Deploy blocked on Base Sepolia | 🔴 |
| BROski-Obsidian-Brain | Truth Pack v2 live — 5 files + front door README | 🟢 |
| hyper-agents-ide | Truth Pack v2.1 added — TRUTH.md + docs/TRUTH_PACK. Live on Render | 🟢 |

---

## 🧠 TRUTH PACK SYNC STATE (Brain A → Brain B)

| Repo | TRUTH.md | docs/TRUTH_PACK/README.md | Last Synced |
|---|---|---|---|
| BROski-Obsidian-Brain | ✅ Source | ✅ Template origin | 2026-05-28 |
| HyperCode-V2.4 | ✅ Added | ✅ Added | 2026-05-28 |
| Hyper-Vibe-Coding-Course | ✅ Added | ✅ Added | 2026-05-28 |
| HyperAgent-SDK | ✅ Added | ✅ Added | 2026-05-28 |
| BROskiPets-LLM-dNFT | ✅ Added | ✅ Added | 2026-05-28 |
| hyper-agents-ide | ✅ Added | ✅ Added | 2026-05-28 |

---

## 🗄️ DATABASE STATE (Supabase `yhtmuibgdnxhbgboajhc`)

- Alembic: up to migration **015** (HyperCode-V2.4 Postgres)
- Supabase tables confirmed: `users`, `mc_missions`, `mc_events`, `mint_nonces`, `token_transactions`
- Security functions fixed → SECURITY INVOKER: `complete_module`, `complete_quest`, `get_or_create_referral_code`
- Edge Functions live: 10 total — see INTEGRATIONS.md for full list
- stripe-webhook: v32 confirmed — do NOT redeploy unless intentional (see INTEGRATIONS.md Stripe section)

---

## ⚡ SPRINT STATUS

| Sprint | Focus | Status |
|---|---|---|
| Sprint 4 | Anon → Signup conversion (`useAnonymousProgress`, `migrateAnonProgress`) | 🟡 Claude shipped — verify pending |
| Next | Wire CatchStragglers.jsx into Mission Control | 🔜 |
| Next | `mc_events` sourcing migration | 🔜 |
| Next | Add `DISCORD_BOT_TOKEN` to Vercel env vars | 🔜 |
| Done ✅ | Truth Pack v1 — 5 files in Brain A (Obsidian) | ✅ 2026-05-28 |
| Done ✅ | Truth Pack v2 — Brain A→B sync, Stripe trap documented, repo entry points | ✅ 2026-05-28 |
| Done ✅ | Truth Pack v2.1 — BROskiPets + hyper-agents-ide entry points complete | ✅ 2026-05-28 |
