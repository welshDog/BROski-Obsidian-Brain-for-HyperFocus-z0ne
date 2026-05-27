# Agent Wishlists (Vault Notes) — Design

## Goal

Create a consistent, Dataview-friendly “wish list” note for each cluster agent, plus a single index note that surfaces them in dashboards.

## Non-Goals

- No code changes.
- No new plugins.
- No changes to existing PARA structure.

## Target Location (Vault)

All notes live in:

- `HYPERFOCUS_ZONE/Agents/`

## Files To Create

- `HYPERFOCUS_ZONE/Agents/Wishlist - hyper-brain-core.md`
- `HYPERFOCUS_ZONE/Agents/Wishlist - mcp-bridge.md`
- `HYPERFOCUS_ZONE/Agents/Wishlist - focus-tracker.md`
- `HYPERFOCUS_ZONE/Agents/Wishlist - morning-briefing.md`
- `HYPERFOCUS_ZONE/Agents/Agent Wishlists (Index).md`

## Frontmatter Standard

Each wishlist note uses the same minimal frontmatter so it can be listed via Dataview.

Required fields:

- `type: agent-wishlist`
- `agent: <agent-name>`
- `status: active`
- `priority_focus: tier-1|tier-2|tier-3`
- `updated: YYYY-MM-DD`

## Content Structure (Per Agent Note)

Each wishlist note uses the same headings to keep scanning fast and dashboards consistent.

- `# Wishlist - <agent-name>`
- `## Role (What I Do)`
- `## What I Want In The Brain (Top 3)`
- `## Inputs I Need (Signals/Data)`
- `## Outputs I Produce (Notes/Events)`
- `## Rules I Must Respect`
- `## Next Upgrades (Tier 1 → Tier 3)`

Tone rules:

- Short sentences.
- Bullets over paragraphs.
- Bold key info where it improves scanability.

## Index Note

The index note provides:

- One short description of what these notes are.
- A Dataview query that lists all `type: agent-wishlist` notes.

Recommended query behavior:

- Sort by `priority_focus` then `updated` (descending).
- Show `agent`, `priority_focus`, `updated`, and a link to the note.

## Acceptance Criteria

- Opening `Agent Wishlists (Index).md` shows all 4 wishlists.
- Each wishlist note has valid frontmatter and consistent headings.
- Notes remain compatible with existing vault + dashboards.

