# Tier 1 Brain Boost Pack (Hub Action Notes) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create 4 Hub action notes (Tools Registry, Decision Log, Today Focus, Focus Metrics Dashboard) with safe content and Dataview blocks where useful.

**Architecture:** Plain Markdown notes under `HYPERFOCUS_ZONE/Hub/`. Tools Registry is fully readable without Dataview. Focus dashboard uses Dataview/DataviewJS to summarize existing focus session notes.

**Tech Stack:** Obsidian Markdown + Dataview plugin (optional rendering).

---

## File Map

**Create**
- `HYPERFOCUS_ZONE/Hub/Tools Registry.md`
- `HYPERFOCUS_ZONE/Hub/Decision Log.md`
- `HYPERFOCUS_ZONE/Hub/Today Focus.md`
- `HYPERFOCUS_ZONE/Hub/Focus Metrics Dashboard.md`

---

### Task 1: Create Tools Registry Note

**Files:**
- Create: `HYPERFOCUS_ZONE/Hub/Tools Registry.md`
- Reference: `cluster.json`
- Reference: `.agents/*/manifest.json`

- [ ] **Step 1: Create the note**

```markdown
---
type: index
title: Tools Registry
status: active
tags: [tools, registry, mcp, agents]
created: 2026-05-27
updated: 2026-05-27
---

# 🧰 Tools Registry

## Safety Rules (Sacred)
- Never write **tokens / secrets** into notes.
- Never log secrets.
- Prefer stable schemas over vibes.
- If unsure, route through **mcp-bridge** only.

## Cluster (Ports + Memory)
| Agent | Port | Memory | Entrypoint |
|---|---:|---|---|
| hyper-brain-core | 3301 | redis | `hyper_brain_core.py` |
| mcp-bridge | 3302 | redis | `mcp_bridge.py` |
| focus-tracker | — | postgres | `focus_tracker.py` |
| morning-briefing | — | redis | `morning_briefing_ai.py` |

## Tool Registry (Static)

### hyper-brain-core
| Tool | Input | Output | Touches |
|---|---|---|---|
| `query_brain` | `query: string` | context text | vault notes |
| `update_brain` | `key: string`, `value: string` | ack | vault notes |

### mcp-bridge
| Tool | Input | Output | Touches |
|---|---|---|---|
| `bridge_call` | `tool: string`, `args: object` | tool result | agent network |

### focus-tracker
| Tool | Input | Output | Touches |
|---|---|---|---|
| `start_session` | `task: string`, `duration_mins: int` | `session_id` | `05-Focus-Sessions/` |
| `end_session` | `session_id: string` | score + log | `05-Focus-Sessions/` |

### morning-briefing
| Tool | Input | Output | Touches |
|---|---|---|---|
| `get_briefing` | `discord_id: string` | briefing text | `00-Inbox/Briefings/` |

## Next Improvements
- Add “Tools Registry” link into `Focus-Command-Center.md`.
```

- [ ] **Step 2: Verify it opens clean in Obsidian**

Expected: readable without Dataview.

---

### Task 2: Create Decision Log Note

**Files:**
- Create: `HYPERFOCUS_ZONE/Hub/Decision Log.md`

- [ ] **Step 1: Create the note**

```markdown
---
type: index
title: Decision Log
status: active
tags: [decisions, architecture, brain]
created: 2026-05-27
updated: 2026-05-27
---

# 🧾 Decision Log

One place for “we decided X because Y”.

## How To Add A Decision (Copy/Paste Template)
- **Date:** YYYY-MM-DD
- **Decision:** One sentence
- **Because:** One sentence
- **Tradeoff:** What we accept
- **Links:** [[note]] [[note]]

---

## Active Decisions

- **2026-05-27** — **Hub action notes** live in `Hub/` because dashboards live there.  
  Because: faster daily scanning.  
  Tradeoff: more Hub docs to maintain.

## Archived Decisions
- (none yet)
```

- [ ] **Step 2: Verify it opens clean in Obsidian**

Expected: copy/paste template is easy to use.

---

### Task 3: Create Today Focus Note

**Files:**
- Create: `HYPERFOCUS_ZONE/Hub/Today Focus.md`

- [ ] **Step 1: Create the note**

```markdown
---
type: dashboard
title: Today Focus
status: active
tags: [today, focus, now-next-later]
created: 2026-05-27
updated: 2026-05-27
---

# 🎯 Today Focus

## NOW (1 thing)
- 

## NEXT (2–3 things)
- 
- 
- 

## LATER (safe parking)
- 
- 

## NOT TODAY (protect the day)
- 
- 

## Closeout (2 minutes)
- [ ] What shipped today?
- [ ] What is the first step for tomorrow?
- [ ] Anything to archive into `04-Archive/`?
```

- [ ] **Step 2: Verify it opens clean in Obsidian**

Expected: fast to fill with bullets.

---

### Task 4: Create Focus Metrics Dashboard Note

**Files:**
- Create: `HYPERFOCUS_ZONE/Hub/Focus Metrics Dashboard.md`
- Reads: `HYPERFOCUS_ZONE/05-Focus-Sessions`

- [ ] **Step 1: Create the note**

```markdown
---
type: dashboard
title: Focus Metrics Dashboard
status: active
tags: [focus, metrics, dashboard]
created: 2026-05-27
updated: 2026-05-27
---

# 📊 Focus Metrics Dashboard

## Last 15 Sessions

```dataview
TABLE created, ended, project, intent, status, actual_minutes, estimated_minutes, mood, difficulty, flow_score, coins_earned, xp_earned
FROM "HYPERFOCUS_ZONE/05-Focus-Sessions"
WHERE contains(file.name, "Session_")
SORT created DESC
LIMIT 15
```

## Last 7 Days (XP + BROski$)

```dataviewjs
const pages = dv.pages('"HYPERFOCUS_ZONE/05-Focus-Sessions"')
  .where(p => p.created && p.xp_earned != null && p.coins_earned != null);

const cutoff = dv.date("today").minus({ days: 7 });
const last7 = pages.where(p => dv.date(p.created) >= cutoff);

const xp = last7.map(p => p.xp_earned).array().reduce((a,b) => a + b, 0);
const coins = last7.map(p => p.coins_earned).array().reduce((a,b) => a + b, 0);

dv.paragraph(`**Last 7 days:** ⭐ ${xp} XP | 💰 ${coins} BROski$`);
```

## How To Read This
- **Flow score** trending up = you’re locking in.
- **Abandoned** sessions are data, not failure.
- **Low file_events + long idle** = friction or distraction.
```

- [ ] **Step 2: Verify Dataview renders**

Expected:
- Table shows recent session notes (at least the existing 2026-05-07 session).
- DataviewJS prints totals (0 is okay if no recent data).

---

## Self-Review Checklist

- [ ] Notes are readable without Dataview.
- [ ] Dataview blocks reference correct folders.
- [ ] No secrets or tokens written anywhere.
- [ ] Links and filenames match vault conventions.

