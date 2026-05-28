# 📦 Truth Pack — Front Door
> **The canonical truth source for the entire HyperCode Ecosystem.**
> Read this folder before touching ANY repo. All 3 brains sync here.
> Updated: 2026-05-28

---

## 🧠 The 3 Brains

| Brain | Type | Owns |
|---|---|---|
| Brain A (Obsidian) | Narrative truth | Decisions, runbooks, status, issues |
| Brain B (Repos / Code) | Executable truth | Configs, schemas, functions, tests |
| Brain C (Live Systems) | Observed truth | Supabase, Vercel, Render, Stripe, logs |

**Rule: All brains read from here. Nothing in Brain B or C overrides Brain A without a proof link.**

---

## 📍 Read These Files (in order)

| # | File | Answers |
|---|---|---|
| 1 | [SYSTEM_STATUS.md](./SYSTEM_STATUS.md) | What is live RIGHT NOW? |
| 2 | [DECISIONS.md](./DECISIONS.md) | Why did we build it this way? |
| 3 | [KNOWN_ISSUES.md](./KNOWN_ISSUES.md) | What’s broken + exact fix? |
| 4 | [RUNBOOKS.md](./RUNBOOKS.md) | How do I do this task? |
| 5 | [INTEGRATIONS.md](./INTEGRATIONS.md) | Where do services connect? |

---

## ✅ Proof Beats Memory Rule

Anything in SYSTEM_STATUS must have ONE of:
- A link to a commit (GitHub URL + SHA)
- A link to a live dashboard screen
- A query result / log excerpt

> No memory. No guesses. No “I think it works.”

---

## 🔄 How To Update After A Session

1. Add bullets to `SYSTEM_STATUS.md` for anything that changed
2. Add a row to `KNOWN_ISSUES.md` for anything that broke
3. Add a row to `DECISIONS.md` if a key architectural choice was made
4. Commit + push — Obsidian Git auto-syncs every 10 mins

---

## 📦 Repos With Truth Pack Entry Points (Brain B sync)

| Repo | TRUTH.md | docs/TRUTH_PACK/ |
|---|---|---|
| BROski-Obsidian-Brain | ✅ Source | ✅ Origin |
| HyperCode-V2.4 | ✅ | ✅ |
| Hyper-Vibe-Coding-Course | ✅ | ✅ |
| HyperAgent-SDK | ✅ | ✅ |
| BROskiPets-LLM-dNFT | ✅ | ✅ |
| hyper-agents-ide | ✅ | ✅ |

---

*Truth Pack — welshDog 🐕🏴󠁧󠁢󠁷󠁬󠁳󠁧⚡ — Brain A canonical source. Last full sync: 2026-05-28*
