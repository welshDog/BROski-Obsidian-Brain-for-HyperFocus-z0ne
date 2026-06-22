# `scripts/` — READ THIS FIRST ⚠️

This folder is a **mixed bag**: some files here are *deprecation stubs* (the real code
moved), and some are *genuinely live tools*. Don't assume a file here is canonical just
because it's here — check the table below.

> 🧠 Architecture rule (load-bearing): the Brain **engine entrypoints live in `.agents/<agent>/`**
> and they **import sibling modules from the repo ROOT**. `scripts/` is a **stale mirror** of
> those modules kept only as loud redirects. Editing a stub here does nothing.

---

## 🔴 Deprecation stubs (DO NOT add code — they `raise ImportError`)

Each of these is a 1-line redirect. Use the **real canonical** instead:

| Stub in `scripts/` | Real canonical location |
|---|---|
| `hyper_brain_core.py` | `.agents/hyper-brain-core/hyper_brain_core.py` |
| `mcp_bridge.py` | `.agents/mcp-bridge/mcp_bridge.py` |
| `morning_briefing_ai.py` | `.agents/morning-briefing/morning_briefing_ai.py` |
| `ai_distraction_filter.py` | repo ROOT `ai_distraction_filter.py` |
| `analytics_engine.py` | repo ROOT `analytics_engine.py` |
| `focus_tracker.py` | repo ROOT `focus_tracker.py` |
| `session_snapshot.py` | repo ROOT `session_snapshot.py` |
| `hyper_split.py` | repo ROOT `hyper_split.py` |
| `github_webhook_server.py` | repo ROOT `github_webhook_server.py` |

> ⚠️ Note: the stub bodies say *"use root … canonical"*, but the three agent entrypoints
> above actually live in `.agents/<agent>/`, not the repo root. Trust this table.
> A duplicate older copy also exists under `brain-bundle-local/agents/` — also NOT canonical.

---

## 🟢 Real tools that genuinely live here (safe to run / edit)

| File | What it does |
|---|---|
| `hyper_brain_ops.py` | Brain Ops engine — OpsLogger, circuit breakers, operation handlers (783 sloc) |
| `github_to_obsidian_v2.py` | Async parallel GitHub→Obsidian vault sync (+ `test_github_to_obsidian_v2.py`) |
| `github_to_obsidian.py` | Older sync — pulls open issues from the welshDog repos → vault |
| `hfz_session_start.py` / `hfz_session_end.py` | HyperFocus session markers + .env/compose checks |
| `hfz_env_guard.py` | Blocks launch if required Brain vars are missing/placeholder |
| `hfz_compose_validator.py` | Enforces Sacred Rules on a docker-compose file |
| `hfz_broski_xp_reward.py` | Publishes an XP award to the Redis `broski_economy` channel |

---

*If you're about to "fix" a Brain module and the file is tiny + raises ImportError —
stop, open the canonical path above instead.*
