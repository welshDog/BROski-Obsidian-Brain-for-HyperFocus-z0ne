# Agent Wishlists (Vault Notes) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add 4 Dataview-friendly agent wishlist notes plus 1 index note to the Obsidian vault.

**Architecture:** Plain Markdown notes stored in `HYPERFOCUS_ZONE/Agents/` with consistent YAML frontmatter and headings. One index note aggregates them using a Dataview table.

**Tech Stack:** Obsidian Markdown + Dataview plugin.

---

## File Map

**Create**
- `HYPERFOCUS_ZONE/Agents/Wishlist - hyper-brain-core.md`
- `HYPERFOCUS_ZONE/Agents/Wishlist - mcp-bridge.md`
- `HYPERFOCUS_ZONE/Agents/Wishlist - focus-tracker.md`
- `HYPERFOCUS_ZONE/Agents/Wishlist - morning-briefing.md`
- `HYPERFOCUS_ZONE/Agents/Agent Wishlists (Index).md`

---

### Task 1: Create Hyper Brain Core Wishlist Note

**Files:**
- Create: `HYPERFOCUS_ZONE/Agents/Wishlist - hyper-brain-core.md`

- [ ] **Step 1: Add the note**

```markdown
---
type: agent-wishlist
agent: hyper-brain-core
status: active
priority_focus: tier-1
updated: 2026-05-27
---

# Wishlist - hyper-brain-core

## Role (What I Do)
- I am the **source-of-truth brain interface**.
- I answer context questions fast.
- I write stable decisions into the vault.

## What I Want In The Brain (Top 3)
- A single **Decision Log** note that is always up to date.
- A single **Now / Next / Later** note for today’s shipping focus.
- A consistent **naming system** for dashboards, maps-of-content, and state files.

## Inputs I Need (Signals/Data)
- Vault “state” notes (streaks, economy, pets, focus sessions).
- Current sprint goals and current shipping target.
- New “wins” after every session.

## Outputs I Produce (Notes/Events)
- Updated `CLAUDE_CONTEXT.md` when context pivots.
- Updated `WHATS_DONE.md` when wins ship.
- A short “today’s focus” summary for dashboards.

## Rules I Must Respect
- Short sentences.
- Bullets over paragraphs.
- **Never break PARA.**
- The vault is the source of truth.

## Next Upgrades (Tier 1 → Tier 3)
- **Tier 1:** Create a dedicated Decision Log and wire updates into the brain update flow.
- **Tier 2:** Add a “context checksum” so stale context is detected.
- **Tier 3:** Auto-generate Maps-of-Content summaries weekly.
```

- [ ] **Step 2: Verify it appears in Obsidian**

Open the file in Obsidian.  
Expected: frontmatter renders clean and headings are intact.

---

### Task 2: Create MCP Bridge Wishlist Note

**Files:**
- Create: `HYPERFOCUS_ZONE/Agents/Wishlist - mcp-bridge.md`

- [ ] **Step 1: Add the note**

```markdown
---
type: agent-wishlist
agent: mcp-bridge
status: active
priority_focus: tier-1
updated: 2026-05-27
---

# Wishlist - mcp-bridge

## Role (What I Do)
- I route tool calls between agents and external systems.
- I keep the agent cluster **talking cleanly**.
- I block unsafe calls.

## What I Want In The Brain (Top 3)
- A single **Tools Registry** note listing supported tools + what they touch.
- A single **Secrets Policy** note (what never enters the vault).
- A clear “allowed integrations” list (GitHub, Discord, Claude, Stripe).

## Inputs I Need (Signals/Data)
- Tool schemas and tool capabilities per agent.
- Runtime environment constraints (ports, networks, rate limits).
- Integration configs stored as variables, not notes.

## Outputs I Produce (Notes/Events)
- A human-readable tool catalog for builders.
- Alert notes when integrations fail.
- A minimal changelog when new tools are added.

## Rules I Must Respect
- Never log secrets.
- Never write tokens into notes.
- Prefer stable schemas over “vibes”.

## Next Upgrades (Tier 1 → Tier 3)
- **Tier 1:** Add a Tools Registry note and enforce naming conventions.
- **Tier 2:** Add integration health notes (GitHub, Discord, LLM).
- **Tier 3:** Add a “tool budget” policy (rate limit + cost guardrails).
```

- [ ] **Step 2: Verify it appears in Obsidian**

Open the file in Obsidian.  
Expected: frontmatter renders clean and headings are intact.

---

### Task 3: Create Focus Tracker Wishlist Note

**Files:**
- Create: `HYPERFOCUS_ZONE/Agents/Wishlist - focus-tracker.md`

- [ ] **Step 1: Add the note**

```markdown
---
type: agent-wishlist
agent: focus-tracker
status: active
priority_focus: tier-1
updated: 2026-05-27
---

# Wishlist - focus-tracker

## Role (What I Do)
- I track **focus sessions**.
- I score session quality.
- I feed streaks and BROski$ rewards.

## What I Want In The Brain (Top 3)
- A single “**Focus Metrics Dashboard**” note with a Dataview table.
- A stable “**Session Template**” that is always used.
- A clear definition of “context switch” and “distraction event”.

## Inputs I Need (Signals/Data)
- Session start/end timestamps.
- Task name, energy state, and difficulty.
- Distraction signals (idle time, app switching, drift).

## Outputs I Produce (Notes/Events)
- Session logs into `05-Focus-Sessions/`.
- Daily rollups into `07-Streaks-Achievements/`.
- Flags for “high-value patterns” and “productivity killers”.

## Rules I Must Respect
- Never shame the user.
- Track patterns, not guilt.
- Prefer simple scoring that is explainable.

## Next Upgrades (Tier 1 → Tier 3)
- **Tier 1:** Ship a Focus Metrics Dashboard note with 3 key metrics.
- **Tier 2:** Add trendlines by week and by project.
- **Tier 3:** Personalised “best focus conditions” recommendations.
```

- [ ] **Step 2: Verify it appears in Obsidian**

Open the file in Obsidian.  
Expected: frontmatter renders clean and headings are intact.

---

### Task 4: Create Morning Briefing Wishlist Note

**Files:**
- Create: `HYPERFOCUS_ZONE/Agents/Wishlist - morning-briefing.md`

- [ ] **Step 1: Add the note**

```markdown
---
type: agent-wishlist
agent: morning-briefing
status: active
priority_focus: tier-2
updated: 2026-05-27
---

# Wishlist - morning-briefing

## Role (What I Do)
- I generate the **daily briefing**.
- I reduce overwhelm.
- I point at the smallest next win.

## What I Want In The Brain (Top 3)
- A single “**Today**” note that acts like a briefing landing page.
- A stable “**Daily Template**” that includes energy and constraints.
- A single “**Blocked List**” note that stays current.

## Inputs I Need (Signals/Data)
- Today’s top tasks + deadlines.
- Overnight GitHub changes (issues, PRs, comments).
- Streak state and focus trends.

## Outputs I Produce (Notes/Events)
- A daily briefing note into `00-Inbox/Briefings/`.
- A 3-item priority list for the day.
- A “one win” recommendation.

## Rules I Must Respect
- No walls of text.
- Always include 1 tiny next step.
- Never overload the day.

## Next Upgrades (Tier 1 → Tier 3)
- **Tier 1:** Create a “Today” landing note and standard briefing format.
- **Tier 2:** Add a “blocked → unblocked” workflow note.
- **Tier 3:** Auto-detect the best project focus based on momentum.
```

- [ ] **Step 2: Verify it appears in Obsidian**

Open the file in Obsidian.  
Expected: frontmatter renders clean and headings are intact.

---

### Task 5: Create Agent Wishlists Index Note

**Files:**
- Create: `HYPERFOCUS_ZONE/Agents/Agent Wishlists (Index).md`

- [ ] **Step 1: Add the note**

```markdown
# Agent Wishlists (Index)

One page. All agent “wants”. Fast scan.

```dataview
TABLE agent AS Agent, priority_focus AS Tier, updated AS Updated
FROM "HYPERFOCUS_ZONE/Agents"
WHERE type = "agent-wishlist"
SORT priority_focus ASC, updated DESC
```
```

- [ ] **Step 2: Verify Dataview renders**

Open the note in Obsidian.  
Expected: a table with 4 rows (one per agent).

---

## Self-Review Checklist

- [ ] All 4 wishlist notes have valid YAML frontmatter.
- [ ] Headings match the standard structure.
- [ ] Index note lists all 4 wishlists via Dataview.
- [ ] No secrets or tokens are written anywhere.

