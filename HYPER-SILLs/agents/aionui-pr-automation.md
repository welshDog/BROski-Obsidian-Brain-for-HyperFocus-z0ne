# 🤖 HYPER-SILL: AionUi PR Automation Pattern

> **Skill ID:** agents/aionui-pr-automation  
> **Source:** iOfficeAI/AionUi `.claude/skills/pr-automation/`  
> **Verified:** ✅ 2026-06-03 via GitHub read  
> **Tags:** #agents #pr #automation #mission-control #hyper-sill  
> **Skill type:** Agent workflow automation

---

## 🎯 What This Skill Does

Automates the full PR lifecycle using a **label-based state machine**:
1. Daemon polls open PRs on a schedule
2. Reviews code automatically via agent
3. Fixes issues raised in the review
4. Merges when all checks pass

In AionUi this is triggered by `/pr-automation` or the `pr-automation.sh` daemon script.

---

## 💻 The Pattern

```
PR opened
  → [label: bot:needs-review]
  → Agent reviews PR → leaves comments
  → [label: bot:needs-fix]
  → Agent fixes issues → commits + pushes
  → [label: bot:ready-to-merge]
  → Agent verifies CI green
  → Agent merges PR
  → [label: bot:merged]
```

Each label is a state. The daemon checks labels and routes to the correct agent action.

---

## 🚀 HyperFocus Z0ne Application

### Where to wire this in:
- **Mission Control** — add a `CatchStragglers` label-state panel showing PR states
- **HyperCode-V2.4** — add `pr-automation.sh` daemon to the agent container stack
- **BROski Orchestrator** — assign the review + fix + merge steps as agent tasks

### Implementation steps:
- [ ] Create `pr-automation.sh` daemon in HyperCode-V2.4 scripts/
- [ ] Define label state machine: `bot:needs-review`, `bot:needs-fix`, `bot:ready-to-merge`, `bot:merged`
- [ ] Wire BROski Orchestrator to handle each label state
- [ ] Add PR automation panel to Mission Control UI
- [ ] Test on a low-risk repo first (e.g. BROski-Obsidian-Brain)

---

## ⚠️ Gotchas

- Label state machine breaks if labels are renamed — treat label names as Sacred
- Daemon must check CI status before merging — never merge a red build
- Agent fix loop can spiral if CI is flaky — add a max-retry limit (3 attempts)
- Always `git fetch` before agent pushes — auto-commits may be running in parallel

---

## 🔗 Source
- [AionUi pr-automation skill](https://github.com/iOfficeAI/AionUi/tree/main/.claude/skills)
- [AIONUI_VS_HYPERAGENT_SDK_2026-06-03.md](../HYPERFOCUS_ZONE/AIONUI_VS_HYPERAGENT_SDK_2026-06-03.md)

---

*This is a HYPER-SILL. Read it before building. Check WHATS_DONE.md before rebuilding.*
