---
created: 2026-09-01
tags: [resource, audit, hyper-merge, ecosystem, safety, ci]
status: active
priority: high
---

# Hyper Merge — Audit Chain

Canonical home for the cross-ecosystem audit chain. These documents review the **Hyper Merge**
(HyperCode-V2.4, HyperAgent-SDK, Hyper-Vibe Coding Course, BROskiPets-LLM-dNFT,
BROski-Obsidian-Brain) as one system. Committed here 2026-09-01; the originals were loose files
in `HperCore/` (not a git repo).

## Read in this order

| # | Document | Lens | Evidence basis |
|---|---|---|---|
| 1 | `01-deep-dive-audit-ecosystem-view-2026-09-01.md` | What **exists** across the repos | File/folder inventory |
| 2 | `02-counter-audit-what-runs-2026-09-01.md` | What actually **runs** | Clones at HEAD `8839ae1b` + `gh` CI history |
| 3 | `03-github-academic-report-2026-09-01.md` | How to **organise** it as a research programme | GitHub profile, health reports, `WHATS_DONE` |
| 4 | `04-synthesis-2026-09-01.md` | **Reconciliation** — conflicts adjudicated, action lists merged | The three above + verified findings |
| 5 | `05-academic-assessment-hypercode-rev1.md` | HyperCode safety-architecture assessment (rev 1) | GitHub API structural inspection |
| 6 | `06-academic-assessment-hypercode-rev2.md` | Same, rev 2 — corrects rev 1, poses the safety-gate question `04` answers | Clone-read + runtime |

**Start with `04-synthesis`** if you only read one — it maps and reconciles the rest.

## The central finding

The distance between *"the system has a safety architecture"* and *"the system enforces
safety"*. Documentation maturity is high; runtime assurance is lower than it suggests. The
next phase is converting documented intention into continuously verified guarantees.

## Canonical evidence scale (used from `04` onward)

| Grade | Meaning |
|---|---|
| A | Live and independently verified |
| B | Automated-test verified |
| C | Implemented but not wired into the load-bearing path |
| D | Documented intention or scaffold |
| E | Known failure, outage, or unresolved risk |

## This-week actions (from `04` §6)

1. Get **one** required check green on `main` in HyperCode — diagnose the `0s` failures.
2. Move `Hyper-Vibe/frontend/.github/workflows/playwright.yml` to the repo root so its 25 specs run.
3. Decide the Safety Shepherd gate — enforce + flip off `monitor`, or record a firm flip date.

## Status snapshot (2026-09-01, HEAD `8839ae1b`)

| Item | Grade |
|---|---|
| HyperCode CI health | E |
| `safety_gate` shipped in `monitor` default | E |
| Strict fail-closed safety client | C |
| Safety contract tests | B |
| SDK ↔ course `hyper-agent-spec.json` alignment | E |
| meta-research-architect | C / D |
| Engineering / self-audit loop | A |
