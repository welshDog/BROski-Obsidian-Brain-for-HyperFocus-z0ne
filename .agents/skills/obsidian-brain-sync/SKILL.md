---
name: obsidian-brain-sync
description: Manages and syncs the BROski Obsidian Brain knowledge vault for
  the Hyperfocus z0ne ecosystem. Use when updating brain docs, syncing sprint
  plans, adding new knowledge nodes, or keeping the meta-layer up to date.
---

# obsidian-brain-sync Skill

## When to use
- Updating CLAUDE.md, CLAUDE_CONTEXT.md, or WHATS_DONE.md after a sprint.
- Adding new ecosystem knowledge nodes or project maps.
- Syncing sprint plans (e.g. HYPER_ECOSYSTEM_PLAN_MAY4.md) after milestones.
- Reviewing or restructuring the brain vault structure.

## Sacred rules (always apply)
- Short sentences. No walls of text.
- Bold key info. Use bullet points.
- PowerShell first for any commands.
- Never debate or change the sacred rules.

## Brain file hierarchy
- `CLAUDE.md` — Master brain. Architecture, rules, container status.
- `CLAUDE_CONTEXT.md` — Current context snapshot for agents.
- `WHATS_DONE.md` — Milestone tracker. Update after every win.
- `HYPER_ECOSYSTEM_PLAN_*.md` — Sprint + roadmap plans.
- `pets_page_deepdive_plan.md` — BROskiPets feature deep dives.

## After every sprint — update flow
1. Open `WHATS_DONE.md`. Add new wins at the top.
2. Open `CLAUDE_CONTEXT.md`. Update current sprint focus.
3. If architecture changed: update `CLAUDE.md` architecture section.
4. Commit with a clear message:
   ```powershell
   git commit -m "🧠 Brain sync: [what changed] — [date]"
   ```
5. Push to main.

## Adding a new knowledge node
1. Create a new `.md` file in the relevant vault folder.
2. Add frontmatter:
   ```md
   ---
   tags: [ecosystem, sprint, pets, sdk, course]
   created: YYYY-MM-DD
   status: active
   ---
   ```
3. Link it from `CLAUDE_CONTEXT.md` or the relevant plan file.

## Success criteria
- All brain files reflect current system state.
- No stale sprint goals left in CLAUDE_CONTEXT.md.
- WHATS_DONE.md shows the latest milestone at the top.
- Vault is clean, linked, and agent-readable.
