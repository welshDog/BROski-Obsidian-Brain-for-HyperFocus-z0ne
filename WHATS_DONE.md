# WHATS_DONE.md -- BROski Obsidian Brain

> Single source of truth. Check this before building ANYTHING.
> Last updated: 2026-06-11

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
| Container hot-patch | RESOLVED | Image rebuilt with Phase 3+4 baked in (2026-06-10), rebuilt again 2026-06-11 for the constellation page — no stale-image risk left |

## Graph Memory Hub Phase 4 (ADDED 2026-06-10 -- DONE, do not rebuild)

| Thing | Status | What it is |
|---|---|---|
| Mentions layer in `graph_builder.py` | DONE | Cross-layer note->code edges when note text names a module (underscore + hyphen spellings). graph.json v3 = 103 nodes / 132 edges (50 mentions edges) |
| `related_nodes()` multi-hop expansion | LIVE | 2 hops, 0.4 decay, score = hop_weight * (1 + centrality), walks wikilink + mentions edges |
| `/graph/related/{id}` for ANY node | LIVE | Code ids return the notes that document them (e.g. `hyper_brain_core` -> Decision Log, Dashboard, Focus-Command-Center, Brain-Constellation-Live); responses include `related_code` too |
| RAG inherits it | LIVE | `query_vault` graph expansion now rides the same multi-hop walk |

NOTE: hot-patch RESOLVED -- image rebuilt 2026-06-10 with Phase 3+4 baked in. (Docker engine crashed under build load 2026-06-10 (8GB box); full Docker Desktop restart fixed it.)

## Graph Memory Hub Phase 5 (ADDED 2026-06-11 -- DONE, do not rebuild)

| Thing | Status | What it is |
|---|---|---|
| HYPER-SILLs as graph layer 3 | LIVE (Brain 1fa192f) | `graph_builder.py` indexes the skills vault (`BRAIN_SKILLS_PATH` or sibling `../HYPER-SILLs-By-WelshDog`): 89 `skill:HS-###` nodes, GoS frontmatter -> `skill-link` edges, skill->code + note->skill `mentions`. graph.json v4 = 192 nodes / ~400 edges, ZERO phantom skills (alias resolution + FRUGAL ENGINE registered, SILLs 171ca84) |
| `/graph/related/{id}` returns `related_skills` | LIVE | For ANY node -- proof: `hyper_brain_core` -> HS-017, HS-011, HS-016, HS-124, HS-125 |
| Skills layer is container-safe | DONE | Unreachable skills path = layer preserved, never wiped |

## Morning Briefing graph citations (ADDED 2026-06-11 -- DONE, do not rebuild)

| Thing | Status | What it is |
|---|---|---|
| `skip_context=False` in `_get_ai_prioritization` | LIVE (Brain ef5060d) | AI prioritization runs through graph-aware RAG -- suggestions grounded in real vault notes. Proof: `/generate` cited 3 real notes in 92s |
| `sources` + `skills` in `ai_suggestions` | LIVE | New `related_skills()` on RemoteMCPBridge pulls skill-layer neighbours of the cited notes; vault briefing note renders "Grounded in" wikilinks + linked skills |
| Agent bridge timeout 90s -> 240s | DONE | Cold tinyllama load blew the old 90s budget (bridge's own `OLLAMA_TIMEOUT_S` is 180s) |
| Bot Brain Citations embed field | LIVE (V2.4 1dfc139) | 7am DM + `/brain-briefing` now show cited notes + skills; bot `/generate` timeout 15s -> 270s (15s guaranteed the fallback embed on the RAG path) |

## Graph Memory Hub Phase 6 — skill routing (ADDED 2026-06-11 -- DONE, do not rebuild)

| Thing | Status | What it is |
|---|---|---|
| `GET :3302/route?query=&limit=` | LIVE (Brain 1e35059) | Deterministic skill router (no LLM): bidirectional word-stem match across ALL node layers seeds a 2-hop expansion -> ranked HYPER-SILLs + supporting notes/code. Proof: "docker healthcheck" -> ⏳ HEALTH WAITER; "orchestrate a new agent" -> THE CREW CHARTER / THE CONDUCTOR / THE THRONE LADDER / THE SACRED SIX |
| crew-orchestrator consumer | LIVE (V2.4 afd9129) | Every `/execute` injects a "[Routed skills]" block into agent prompts (`GRAPH_ROUTE_URL` env, 5s timeout, fail-open); routed ids stored in task details; `GET :8081/route/preview?q=` = auth-gated zero-LLM dry-run |
| Build-context fix | DONE (V2.4 afd9129) | crew-orchestrator compose context was repo root: 3.85GB context transfer per build + would produce a BROKEN image (root has no main.py, wrong requirements.txt). Now `./agents/crew-orchestrator` |

## Brain Constellation page (ADDED 2026-06-11 -- DONE, do not rebuild)

| Thing | Status | What it is |
|---|---|---|
| `GET :3302/constellation` | LIVE (Brain edba235) | D3 force-graph of graph.json served same-origin by agent-mcp-bridge (no CORS, no new container). 192 stars: notes violet / skills gold / code cyan, radius by centrality |
| Interactions | LIVE | Hover = neighbourhood focus, click = side panel fed by `/graph/related/{id}` (related notes/code/skills, click-through), legend chips toggle layers, search, drag/zoom/pan, reduced-motion safe |
| Proof | Playwright headless | 192 circles rendered, panel opens on hyper_brain_core with 5 related skills, zero console errors |
| NOT the same as | -- | `constellation_builder.py` (markdown status note) and the `hyperfocus-constellation` GitHub Pages showcase are different things -- all three are wanted |

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
