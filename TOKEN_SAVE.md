# ⚡ TOKEN_SAVE — BROski-Obsidian-Brain
> Paste this at the start of any AI session. ~100 tokens. Replaces full history.
> Update after every task. Keep it short.

---

## 🧠 Session State
DATE: 2026-06-18
GOAL: [one sentence — fill in at session start]
STATUS: 3 Brain agents LIVE (ports 3301/3302/3303, profile: brain-agents) · Obsidian vault + GitHub bridge active
LAST COMMIT: [fill in]
NEXT ACTION: [fill in — check CLAUDE.md + WHATS_DONE.md]
BLOCKERS: [none / describe]

---

## 📋 Prompt Template (copy-paste to start any AI session)
```
Repo: BROski-Obsidian-Brain
State: [paste SESSION STATE block above — ~70 tokens]
Task: [one sentence]
Rules: CLAUDE.md applies. PARA vault structure. GitHub bridge via scripts/github_to_obsidian.py. Keep replies short. Bullets first.
```

---

## 🔗 Key Files
- Constitution: `CLAUDE.md`
- Never rebuild: `WHATS_DONE.md`
- Vault sync: `scripts/github_to_obsidian.py`
- Brain agents: `cluster.json` + `.agents/` (ports 3301/3302/3303)

---

## ⚡ Token-Saving Rules
- Send this file, NOT full CLAUDE.md
- Fetch only the vault note or script needed
- This repo is the memory layer — use it to REDUCE context in other repos
- Ask for bullets only, max 5 lines unless deeper needed

---
*Part of the HyperFocus Z0ne Token-Saving Blueprint — built by @welshDog 🏴󠁧󠁢󠁷󠁬󠁳󠁥*
