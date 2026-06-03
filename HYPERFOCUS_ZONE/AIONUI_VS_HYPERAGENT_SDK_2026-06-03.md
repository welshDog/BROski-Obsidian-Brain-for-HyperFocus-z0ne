# 🤯 AionUi ACP vs HyperAgent-SDK — Deep Dive

> **Source:** Live GitHub read — iOfficeAI/AionUi verified  
> **Captured:** 2026-06-03  
> **Tags:** #aionui #hyperagent-sdk #agents #architecture #deep-dive #course  
> **Protocol:** See [DATA_TO_BRAIN_PROTOCOL.md](./DATA_TO_BRAIN_PROTOCOL.md)  
> **Verified:** ✅ AionUi AGENTS.md + root structure read directly from GitHub

---

## 🎯 The Headline

AionUi (27,485 stars) and HyperAgent-SDK are **solving the same problem from different angles**.
- AionUi = polished desktop platform for running 20+ AI agents together
- HyperAgent-SDK = flexible SDK layer for writing agents once and deploying everywhere

Both built independently. Both converged on almost identical patterns. This is validation. 🏆

---

## 📊 Architecture Comparison

| Dimension | AionUi ACP | HyperAgent-SDK |
|---|---|---|
| **What it is** | Desktop app — runs Claude, Codex, Gemini CLI + 20 agents in one UI | npm package — write agents once, deploy anywhere |
| **Stack** | TypeScript, Bun, Electron (desktop) | Node.js, TypeScript |
| **Agent contract** | `.claude/skills/` — structured skill files per agent | `manifest.json` — manifest-driven agent definitions |
| **Skills system** | AGENTS.md Skills Index — named skills with triggers | HYPER-SILLs vault — 72+ hero-named skills |
| **Coordination** | ACP (Agent Coordination Protocol) — queue + team mode | Swarm coordination via manifest + shared interface |
| **Process isolation** | Main vs Renderer — strict IPC bridge | Docker profile isolation (agents-net, pets, brain) |
| **Deployment** | Local desktop — always-on 24/7 cowork | Cloud + Docker — cross-repo, cross-platform |
| **Validation** | `--strict` lint, `just push` gate, Vitest 80% coverage | `--strict` validation mode |
| **PR/agent workflow** | `oss-pr`, `pr-ship`, `pr-automation` skills | Manual + GitHub connector |
| **Licence** | MIT | MIT |

---

## 🤯 The Big Reveal — Same Vision, Built Independently

Both systems have:
- **Named skills that trigger agent behaviour** — AionUi calls them `.claude/skills/`, we call them HYPER-SILLs
- **A strict write-once, run-anywhere agent contract** — AionUi uses ACP queue, we use manifest.json
- **Hard separation rules** — AionUi: Main vs Renderer. Us: Docker profiles, never cross-contaminate
- **Push gates** — AionUi: `just push` enforces lint + test + typecheck. Us: `git fetch` + commit rule

---

## 🔥 What AionUi Has That We Don’t (Yet)

| Feature | AionUi | Ours |
|---|---|---|
| `pr-automation` skill | Daemon polls PRs, reviews, fixes, merges via label state machine | Manual |
| `pr-ship` skill | Full end-to-end PR lifecycle in one command | Manual |
| `pr-verify` skill | Verifies + merges PRs with impact analysis | Healer Agent (partial) |
| Vitest 80% coverage gate | Hard enforced | Not enforced yet |
| Directory size limit (max 10) | Hard rule in AGENTS.md | Not formalised |
| i18n skill | Full internationalisation workflow | Not relevant yet |

---

## 🚀 What We Have That AionUi Doesn’t

- **ND-first design** — built for ADHD/dyslexic/autistic brains. AionUi is generic dev tooling
- **BROski$ economy** — XP, tokens, gamification, streaks. AionUi has zero gamification
- **HyperSplit engine** — ADHD-safe task decomposition. Unique to us
- **Course + platform fusion** — AionUi is a tool. We’re a full learning ecosystem
- **BROskiPets + Web3 layer** — gamified identity. AionUi doesn’t go near this
- **Mission Control** — ops dashboard. AionUi has no equivalent

---

## 💡 Best Things to Steal from AionUi

1. **`pr-automation` skill pattern** → wire into Mission Control as an agent task
2. **`pr-ship` skill** → add to HYPER-SILLs as `agents/pr-ship.md`
3. **Directory size limit rule** (max 10 children) → add to HYPER-SILLs vault structure rules
4. **IPC bridge pattern** → apply to HyperCode’s process isolation between containers
5. **80% test coverage gate** → add to HyperCode-V2.4 CI pipeline

---

## ⚡ HyperSplit Micro-Actions

- [ ] Add `agents/aionui-pr-automation.md` to HYPER-SILLs — done in this commit
- [ ] Add `agents/aionui-pr-ship.md` to HYPER-SILLs — done in this commit
- [ ] Update M6 Agent Architecture module to reference AionUi ACP vs HyperAgent-SDK
- [ ] Read AionUi `docs/architecture/overview.md` for full ACP deep-dive
- [ ] Consider adding 80% Vitest coverage gate to HyperCode-V2.4

---

## 🔗 Source Links

- [AionUi GitHub](https://github.com/iOfficeAI/AionUi)
- [AionUi AGENTS.md](https://github.com/iOfficeAI/AionUi/blob/main/AGENTS.md)
- [AionUi docs/README.md](https://github.com/iOfficeAI/AionUi/blob/main/docs/README.md)
- [HyperAgent-SDK](https://github.com/welshDog/HyperAgent-SDK)
- [FUTURE_STACK_DISCOVERY_2026-06-03.md](./FUTURE_STACK_DISCOVERY_2026-06-03.md)

---

*Nice one BROski♾️ — you built the same vision as a 27k-star project. Now steal the best bits.*
