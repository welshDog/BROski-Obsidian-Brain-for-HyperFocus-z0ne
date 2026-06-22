# LOOP_LEVEL_SPEC.md — Brain Level Loop Template
> 🏁 Levels 18/19/20 are all DONE (see LOOP_CONTEXT). This is now a REFERENCE
> template + record of how they were built — reuse the shape for any future level.

---

## Level Loop Prompt Shape

**REPO:** BROski-Obsidian-Brain
**GOAL:** Complete Level [18 | 19 | 20]: [Level Name]
**SUCCESS TEST:** [Specific health check or function test]

### Level 18 — AI Distraction Filter ✅ DONE (2026-06-20)
- File: `aidistractionfilter.py` (wired into :8100 — 3 signals → Discord nudge)
- Wire to: `sessionsnapshot.py`
- Monitor: vault note activity, idle time, topic drift
- Intervention: BROski nudge notification + session re-focus prompt
- Success: filter nudge fires on vault idle > 10 minutes

### Level 19 — DifficultyDial Dynamic XP ✅ DONE (2026-06-20)
- Build: user-adjustable filter intensity (low / medium / hyper)
- Dynamic XP: variable reward multipliers based on session quality
- Connect to: BROski economy + HyperSplit chunk difficulty scoring
- Success: XP multiplier changes based on session quality score

### Level 20 — THE HYPER BRAIN Constellation ✅ DONE (2026-06-11)
- Live at `:3302/constellation` (also `/route` + pet brain-feed)
- What: unified visual map of ENTIRE ecosystem
- All 5 repos visible as nodes — vault, engine, NFTs, economy, courses
- Success: Constellation renders, all 5 repo nodes navigable ✅
