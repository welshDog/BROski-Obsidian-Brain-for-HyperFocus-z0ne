# 🚀 HYPER-SILL: AionUi PR Ship Pattern

> **Skill ID:** agents/aionui-pr-ship  
> **Source:** iOfficeAI/AionUi `.claude/skills/pr-ship/`  
> **Verified:** ✅ 2026-06-03 via GitHub read  
> **Tags:** #agents #pr #workflow #automation #hyper-sill  
> **Skill type:** Agent workflow automation

---

## 🎯 What This Skill Does

`pr-ship` is a **single-command, end-to-end PR lifecycle skill**. You trigger it once and the agent:
1. Creates the branch
2. Commits the code
3. Waits for CI to pass
4. Reviews the PR
5. Fixes any issues
6. Merges the PR

In AionUi this is triggered by `/pr-ship` after development is complete.

---

## 💻 The Pattern

```
/pr-ship triggered
  → git checkout -b feat/branch
  → git commit + push
  → Create PR via GitHub API
  → Poll CI status → wait for green
  → Run pr-review → collect issues
  → If issues: run pr-fix → commit + push
  → Re-check CI → green?
  → Merge PR
  → Done ✨
```

---

## 🚀 HyperFocus Z0ne Application

### Where to wire this in:
- **BROski Orchestrator** — add `/pr-ship` as a slash command in Discord bot
- **Mission Control** — add a one-click “Ship It” button that triggers this flow
- **HyperAgent-SDK** — add `pr-ship` as a named agent workflow in manifest.json

### Implementation steps:
- [ ] Add `pr-ship` agent workflow to HyperAgent-SDK manifest.json
- [ ] Add `/pr-ship` slash command to Discord bot (BROski Orchestrator)
- [ ] Add “Ship It” button to Mission Control UI panel
- [ ] Wire CI polling into the ship flow (check GitHub Actions status)
- [ ] Add max-retry guard (3 fix attempts before human escalation)

---

## 🧠 ADHD-Friendly Note

This skill is perfect for hyperfocus coding sessions. You build the thing, say `/pr-ship`, and the agent handles the rest. No context-switching. No remembering the PR checklist. No forgetting to push. ⚡

---

## ⚠️ Gotchas

- Never trigger `/pr-ship` on `main` directly — always needs a feature branch
- CI must be configured before this works — no CI = no gate = dangerous
- Agent commit messages must follow `feat/fix/chore: description` format — no AI signatures
- `git fetch` before any agent push — auto-commits may be running

---

## 🔗 Source
- [AionUi AGENTS.md Skills Index](https://github.com/iOfficeAI/AionUi/blob/main/AGENTS.md)
- [AIONUI_VS_HYPERAGENT_SDK_2026-06-03.md](../HYPERFOCUS_ZONE/AIONUI_VS_HYPERAGENT_SDK_2026-06-03.md)

---

*This is a HYPER-SILL. Read it before building. Check WHATS_DONE.md before rebuilding.*
