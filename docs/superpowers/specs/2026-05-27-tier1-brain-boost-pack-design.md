# Tier 1 Brain Boost Pack (Hub Action Notes) — Design

## Goal

Add 4 action notes into the vault Hub that turn agent wishlists into daily execution and system clarity.

## Non-Goals

- No code changes.
- No new Obsidian plugins.
- No restructuring of PARA folders.
- No automation that depends on external services.

## Location

All new notes live in:

- `HYPERFOCUS_ZONE/Hub/`

## Files To Create

- `HYPERFOCUS_ZONE/Hub/Tools Registry.md`
- `HYPERFOCUS_ZONE/Hub/Decision Log.md`
- `HYPERFOCUS_ZONE/Hub/Today Focus.md`
- `HYPERFOCUS_ZONE/Hub/Focus Metrics Dashboard.md`

## Conventions

- Short sentences.
- Bullets over paragraphs.
- Dataview blocks where they add instant value.
- Keep content safe: never store secrets, tokens, or private identifiers.

## Note Designs

### Tools Registry

Purpose:

- One place to list: agent → tools → what they touch → safety rules.

Content:

- Cluster overview (from `cluster.json` + manifests).
- A Dataview-free static registry table (stable even if Dataview breaks).
- Safety rules at top.

### Decision Log

Purpose:

- Single source of truth for “we decided X because Y”.

Content:

- Template row format for decisions.
- Links to related notes.
- A section for active decisions vs archived decisions.

### Today Focus (Now/Next/Later)

Purpose:

- Protect the day from drift.

Content:

- Now / Next / Later sections.
- A “Not Today” list.
- A 2-minute end-of-day closeout checklist.

### Focus Metrics Dashboard

Purpose:

- A minimal metrics view based on existing session notes in `05-Focus-Sessions/`.

Content:

- A Dataview table of the last N sessions with key fields.
- A DataviewJS block to sum XP and coins for the last 7 days.
- A short “How to read this” section.

## Acceptance Criteria

- Notes open cleanly and are readable even without Dataview.
- If Dataview is enabled, dashboard tables render with real data.
- No secrets are written anywhere.

