# 📦 TRUTH PACK — Repo Sync Pointer

> **This repo does NOT own the source of truth.**
> All canonical state lives in the Obsidian Brain vault.

---

## 📍 Canonical Truth Location

**Obsidian Brain repo:**
https://github.com/welshDog/BROski-Obsidian-Brain-for-HyperFocus-z0ne/tree/main/HYPERFOCUS_ZONE/Hub/Truth-Pack/

### Files (read in this order)

| File | What it answers |
|---|---|
| [`SYSTEM_STATUS.md`](https://github.com/welshDog/BROski-Obsidian-Brain-for-HyperFocus-z0ne/blob/main/HYPERFOCUS_ZONE/Hub/Truth-Pack/SYSTEM_STATUS.md) | What is live RIGHT NOW? |
| [`DECISIONS.md`](https://github.com/welshDog/BROski-Obsidian-Brain-for-HyperFocus-z0ne/blob/main/HYPERFOCUS_ZONE/Hub/Truth-Pack/DECISIONS.md) | Why did we do it this way? |
| [`RUNBOOKS.md`](https://github.com/welshDog/BROski-Obsidian-Brain-for-HyperFocus-z0ne/blob/main/HYPERFOCUS_ZONE/Hub/Truth-Pack/RUNBOOKS.md) | How do I do this task? |
| [`KNOWN_ISSUES.md`](https://github.com/welshDog/BROski-Obsidian-Brain-for-HyperFocus-z0ne/blob/main/HYPERFOCUS_ZONE/Hub/Truth-Pack/KNOWN_ISSUES.md) | What's broken + how to unblock? |
| [`INTEGRATIONS.md`](https://github.com/welshDog/BROski-Obsidian-Brain-for-HyperFocus-z0ne/blob/main/HYPERFOCUS_ZONE/Hub/Truth-Pack/INTEGRATIONS.md) | Where do things connect? |

---

## 🧠 The 3 Brains Rule

| Brain | Type | Owns |
|---|---|---|
| Brain A (Obsidian) | Narrative truth | Decisions, runbooks, status, issues |
| Brain B (Repos / Code) | Executable truth | Configs, schemas, functions, tests |
| Brain C (Live Systems) | Observed truth | Supabase, Vercel, Render, Stripe, Logs |

**Rule: Repos read from Brain A. They never invent narrative truth.**

---

## ✅ Proof Beats Memory

Anything added to SYSTEM_STATUS must have one of:
- A link to code (GitHub URL + commit)
- A link to a dashboard screen
- A query result / log excerpt

No memory. No guesses. No "I think it works".

---

## 🔄 How To Sync This Repo Into Truth Pack

After every session, add bullets to `SYSTEM_STATUS.md` for anything that changed:
```
- ✅ [What shipped] — [link to commit or dashboard]
- 🔴 [What broke] — [exact symptom + proof]
```
Then commit + push Obsidian Brain repo.
Obsidian Git auto-commits every 10 mins.

---
*Truth Pack README — welshDog 🐕🏴󠁧󠁢󠁷󠁬󠁳󠁧⚡ — Drop this file into every repo's `docs/TRUTH_PACK/` folder.*
