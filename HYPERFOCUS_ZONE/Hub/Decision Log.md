---
type: decision-log
title: Decision Log
status: active
owner: hyper-brain-core
tags:
  - decisions
  - log
  - brain
created: 2026-05-27
updated: 2026-05-27
---

# 📋 Decision Log

> One place. All stable decisions. Always up to date.

## Rules
- Add a decision when it affects architecture, vault structure, or shipping direction.
- Update `status` when a decision changes — don't delete, move to Archive.
- Keep each entry to 3–5 bullets max.

## Decision Entry Template
```
### DL-YYYY-### — Title
- **Status:** Proposed | Accepted | Rejected | Superseded
- **Date:** YYYY-MM-DD
- **Context:** Why this came up.
- **Decision:** What was decided.
- **Consequences:** What changes as a result.
- **Links:** [[related note]]
```

## Active Decisions

### DL-2026-001 — Use Vite + React for Hyper-Vibe Course (not Next.js)
- **Status:** Accepted
- **Date:** 2026-05-01
- **Context:** Next.js App Router patterns caused build issues with AI agent tooling.
- **Decision:** Vite + React is the standard for `Hyper-Vibe-Coding-Course`. Never generate Next.js/App Router code for this repo.
- **Consequences:** All component patterns, routing, and env vars follow Vite conventions.
- **Links:** [[CLAUDE.md]]

### DL-2026-002 — Use `apply_migration` only (never `supabase db push`)
- **Status:** Accepted
- **Date:** 2026-05-01
- **Context:** Migrations became desynced after a `db push` wiped the migration history.
- **Decision:** All DDL changes go through `apply_migration` via the Supabase MCP tool.
- **Consequences:** No direct `supabase db push` ever. Ever.
- **Links:** [[WHATS_DONE.md]]

### DL-2026-003 — 5-Tier Stripe Pricing (Option A)
- **Status:** Accepted
- **Date:** 2026-05-27
- **Context:** Old 3-tier config had dead price IDs. Webhook was silently failing.
- **Decision:** Replaced with 5-tier stack: Starter £29, Pro £49, Builder £97, Architect £167, Hyper Legend £247.
- **Consequences:** `stripe/products.config.ts` and `stripe-webhook` v39 now reflect these IDs.
- **Links:** [[NEXT_SESSION_HANDOVER_2026-05-27.md]]

## Archive (Superseded / Closed)
_Nothing archived yet._
