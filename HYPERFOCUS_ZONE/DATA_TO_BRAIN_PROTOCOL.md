# 🧠 Data-to-Brain Protocol (v1)

> **Rule:** Every AI explainer output must be captured, tagged, and linked before it's treated as live knowledge.

---

## Why This Exists

NotebookLM, Claude, Perplexity, and other AI tools produce **ephemeral insights** — brilliant in the moment, gone tomorrow. This protocol converts those insights into **permanent, searchable, actionable nodes** in the BROski Brain.

**NotebookLM = The Interviewer** → BROski Brain = The Library

---

## The 5-Step Rule

```
1. CAPTURE   — Save AI answer as a Markdown note in HYPERFOCUS_ZONE/
2. TAG        — Add #notebooklm-import #hfz-map + 1 skill-specific tag
3. LINK       — Link back to PORTAL.md → source repo → specific file
4. SPLIT      — Extract 3 micro-tasks max per note (feed HyperSplit)
5. VERIFY     — Confirm note is not a duplicate of live truth in source repos
```

---

## File Naming Convention

```
NOTEBOOKLM_[TOPIC]_[DATE].md
CLAUDE_[TOPIC]_[DATE].md
PERPLEXITY_[TOPIC]_[DATE].md
```

Examples:
- `NOTEBOOKLM_INSIGHTS.md` (rolling file for general extracts)
- `NOTEBOOKLM_HYPERTOP20_2026-06-03.md`
- `CLAUDE_SPRINT4_REVIEW_2026-06-03.md`

---

## Tagging System

| Tag | When to use |
|---|---|
| `#notebooklm-import` | Any output from NotebookLM |
| `#hfz-map` | Describes ecosystem architecture or repo structure |
| `#hyper-skills` | Relates to HYPER-SILLs vault or hero skills |
| `#boot-protocol` | Relates to AGENT-START, PORTAL, Master Boot Protocol |
| `#broski-economy` | Relates to BROski$ tokens, XP, streaks |
| `#nd-support` | Relates to ADHD/dyslexia/autism support features |
| `#ops` | Relates to Mission Control, mc_events, Catch Stragglers |

---

## Source Links (always include at least 1)

- [PORTAL.md](../PORTAL.md) — Navigation hub
- [AGENT-START.md](../AGENT-START.md) — Boot protocol
- [vault-index.md (HYPER-SILLs)](https://github.com/welshDog/HYPER-SILLs-By-WelshDog) — Skills vault
- [HyperCode-V2.4](https://github.com/welshDog/HyperCode-V2.4) — Core platform
- [Hyper-Vibe-Coding-Course](https://github.com/welshDog/Hyper-Vibe-Coding-Course) — Course platform
- [WelshDog-Mission-Control](https://github.com/welshDog/WelshDog-Mission-Control) — Ops dashboard
- [HyperAgent-SDK](https://github.com/welshDog/HyperAgent-SDK) — Agent orchestration
- [BROskiPets-LLM-dNFT](https://github.com/welshDog/BROskiPets-LLM-dNFT) — NFT economy

---

## System Engine Hooks

### Morning Briefing (`morning_briefing_ai.py`)
Any note in `HYPERFOCUS_ZONE/` tagged `#hfz-map` or `#notebooklm-import` is automatically eligible for inclusion in the daily morning narrative.

### HyperSplit (`hypersplit_engine.py`)
Every Data-to-Brain note should include a `## HyperSplit Tasks` section with **3 micro-tasks max** so HyperSplit can ingest them without cognitive overload.

---

## What This Rule Is NOT

- ❌ Do NOT copy-paste raw AI output without cleaning it up
- ❌ Do NOT treat a Brain note as live truth — always verify against source repo
- ❌ Do NOT skip the LINK step — traceability is non-negotiable
- ❌ Do NOT create duplicate notes — check existing Brain notes first

---

## Rule Ownership

- **Maintained by:** Lyndz / WelshDog
- **Lives in:** `HYPERFOCUS_ZONE/DATA_TO_BRAIN_PROTOCOL.md`
- **Referenced by:** AGENT-START.md, PORTAL.md
- **Version:** v1 — June 2026

---

*Nice one BROski♾️ — every AI interview now makes the Brain stronger.*
