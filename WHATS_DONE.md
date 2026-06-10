# WHATS_DONE.md -- BROski Obsidian Brain

> Single source of truth. Check this before building ANYTHING.
> Last updated: 2026-06-10

---

## Graph Memory Hub (ADDED 2026-06-10 -- Phase 1 DONE, do not rebuild)

| Thing | Status | What it is |
|---|---|---|
| `HYPERFOCUS_ZONE/06-AI-Context/graph.json` | DONE | CANONICAL v1 memory-hub artifact (23 nodes / 31 edges, AST scan 2026-06-09). In containers: `/vault/06-AI-Context/graph.json` |
| `GET :3302/graph` | LIVE | agent-mcp-bridge serves the full artifact (proof: nodes=23, edges=31) |
| `GET :3302/graph/node/{id}` | LIVE | One node + all touching edges (proof: hyper_brain_core -> 13 edges; unknown id -> 404) |
| `BRAIN_GRAPH_PATH` env | DONE | Overrides default graph location in mcp_bridge agent |
| `graphify-out/` | REMOVED | Was a byte-identical duplicate of the canonical copies |
| briefing->mcp-bridge HTTP wiring | DONE 2026-06-09 | Graph report's HIGH issue #1 already resolved -- `:3304/health` shows `connected:true` |

## Graph Memory Hub Phase 2 (ADDED 2026-06-10 -- DONE, do not rebuild)

| Thing | Status | What it is |
|---|---|---|
| `graph_builder.py` | DONE | Stdlib-only notes-layer rebuilder: scans vault wiki-links, merges into graph.json, PRESERVES curated code layer + issues. v2 = 103 nodes / 82 edges (80 notes, 51 wikilinks) |
| `.github/workflows/graph-refresh.yml` | DONE but BLOCKED | Auto-reruns builder on vault .md push; loop-safe ([skip ci] + paths filter). **GitHub Actions account billing lock (2026-06-10) -- jobs won't start until billing fixed.** Covered meanwhile by host task below |
| `HyperBrain-Graph-Refresh` scheduled task | LIVE 2026-06-10 | Windows host task, every 30 min: `C:\Python313\python.exe graph_builder.py`. Remove with `schtasks /delete /tn HyperBrain-Graph-Refresh /f` once Actions billing is unlocked |
| Note node ids | CONVENTION | `note:<basename>` (e.g. `note:Dashboard`); `status: phantom` = wiki-link target with no file yet |
| Live serving | NO REBUILD NEEDED | `/graph` reads the mounted file per request -- regeneration shows up in the API instantly |
| `constellation_builder.py` repo list | FIXED 2026-06-10 | WelshDog-Mission-Control added (graph MEDIUM issue resolved) + 06-AI-Context in VAULT_FOLDERS; lands on next monolith/brain-core rebuild |

## Graph Memory Hub Phase 3 (ADDED 2026-06-10 -- DONE, do not rebuild)

| Thing | Status | What it is |
|---|---|---|
| Graph-aware RAG in `query_vault` | LIVE | Keyword seeds (stopword-filtered + filename-boosted) -> 1-hop wikilink expansion via graph.json -> answers cite real linked notes. Proof: BROskiPets query cited BROskiPets.md + its 2 top graph neighbors, 81s |
| `GET :3302/graph/related/{id}` | LIVE | Deterministic view of the same expansion (no LLM call) -- e.g. `note:BROskiPets` -> HyperCode-V2.4.md, Hyper-Vibe-Course.md, ... |
| RAG budget env knobs | DONE | `RAG_MAX_FILES=3`, `RAG_CHARS_PER_FILE=600`, `RAG_NUM_PREDICT=200`, `OLLAMA_TIMEOUT_S=180` -- this box's CPU Ollama times out on fat prompts; tune via compose env |
| `.agents/mcp-bridge/Dockerfile` layer fix | DONE | requirements.txt copied BEFORE pip install -- code-only rebuilds no longer need PyPI |
| ⚠️ Container is HOT-PATCHED | ACTION NEEDED | PyPI DNS was down from buildkit 2026-06-10; Phase 3 code deployed via `docker cp` + restart. **Image is stale — run `docker compose --profile brain-agents up -d --build agent-mcp-bridge` when network recovers**, else a recreate reverts the seeder/timeout fixes |

## Graph Memory Hub Phase 4 (ADDED 2026-06-10 -- DONE, do not rebuild)

| Thing | Status | What it is |
|---|---|---|
| Mentions layer in `graph_builder.py` | DONE | Cross-layer note->code edges when note text names a module (underscore + hyphen spellings). graph.json v3 = 103 nodes / 132 edges (50 mentions edges) |
| `related_nodes()` multi-hop expansion | LIVE | 2 hops, 0.4 decay, score = hop_weight * (1 + centrality), walks wikilink + mentions edges |
| `/graph/related/{id}` for ANY node | LIVE | Code ids return the notes that document them (e.g. `hyper_brain_core` -> Decision Log, Dashboard, Focus-Command-Center, Brain-Constellation-Live); responses include `related_code` too |
| RAG inherits it | LIVE | `query_vault` graph expansion now rides the same multi-hop walk |

NOTE: still HOT-PATCHED (see Phase 3 row) -- the rebuild-when-PyPI-works action now picks up Phase 3 + 4 together. Docker engine crashed under build load 2026-06-10 (8GB box); full Docker Desktop restart fixed it.

Phase 5 ideas (NOT done): embed-based seeding when a GPU exists; graph-aware skill discovery from HYPER-SILLs; serve graph view in Brain web/ UI.

## Core Python Brain Tools (ALL EXIST -- do not rebuild)

| File | Status | What it does |
|---|---|---|
| `hyper_brain_core.py` | DONE | Core brain engine, knowledge retrieval |
| `focus_tracker.py` | DONE | Focus session tracking + state |
| `analytics_engine.py` | DONE | Productivity analytics + heatmaps |
| `morning_briefing_ai.py` | DONE | Daily AI briefing generator |
| `mcp_bridge.py` | DONE | MCP bridge (runs on :8823) |
| `session_snapshot.py` | DONE | Saves session state to vault |
| `constellation_builder.py` | DONE | Knowledge graph from Obsidian notes |
| `ai_distraction_filter.py` | DONE | AI-powered distraction detection |
| `gamification_summary.py` | DONE | XP, levels, BROski tokens |
| `events_feed.py` | DONE | Events stream |
| `github_webhook_server.py` | DONE | GitHub webhook listener |
| `difficulty_dial.py` | DONE | Task difficulty adjustment |
| `hyper_split.py` | DONE | Vault note splitter |
| `AIFS-LAUNCH.ps1` | DONE | AI File System launcher |

## PSAI + aish Integration (ADDED 2026-06-03)

| File | Status | What it does |
|---|---|---|
| `PSAI-Register-Tools.ps1` | NEW | Registers all 10 brain tools as PSAI agent-callable functions |
| `aish-mcp-config.json` | NEW | Wires aish to mcp_bridge.py + HyperCode gateway |
| `BROski-Brain-Quick-Start.ps1` | NEW | One-script boot: deps + MCP bridge + PSAI tools |

## Vault Structure

| Folder | Status | What it is |
|---|---|---|
| `HYPERFOCUS_ZONE/` | DONE | Main vault -- course reviews, project notes |
| `HYPER-SILLs/` | DONE | Skills + learning notes |
| `sessions/` | DONE | Session snapshots |
| `Ops-Logs/` | DONE | Operational logs |
| `.obsidian/` | DONE | Obsidian config |
| `.agents/` | DONE | Agent configs |
| `.claude/` | DONE | Claude context files |

## Key Docs

| File | What it is |
|---|---|
| `AGENT-START.md` | Agent onboarding + skill load |
| `CLAUDE.md` | Sacred rules for AI partners |
| `CLAUDE_CONTEXT.md` | Extended Claude context |
| `ANALYSIS_AND_ROADMAP.md` | Full roadmap |
| `UPGRADE_COMPLETE_SUMMARY.md` | Previous upgrade history |
| `NEXT_SESSION_HANDOVER_2026-06-02.md` | Last handover |

## DO NOT rebuild

- Any Python file listed above -- they exist and work
- `.obsidian/` config -- already tuned
- `cluster.json` -- knowledge graph config
- `docker-compose.hyper-brain.yml` -- brain Docker setup
