---
generated: 2026-06-09
tool: brain-graph-analysis (AST + static import trace)
root: BROski-Obsidian-Brain-for-HyperFocus-z0ne
nodes: 23
edges: 31
---

# 🧠 Brain Repo — Knowledge Graph Report

> Generated 2026-06-09 by AST static analysis (graphify equivalent).
> Source of truth: imports in `.agents/` + root scripts + AIFS layer.

---

## 🗺️ Topology Overview

The repo has **four distinct layers** — monolith engine, standalone agents, AIFS, and a stale mirror.

```
┌─────────────────────────────────────────────────────┐
│  MONOLITH (port 8100)                               │
│  hyper_brain_core.py ──imports──► 10 engine scripts │
└─────────────────────────────────────────────────────┘
         │
         │  same code, separate containers
         ▼
┌──────────────────────────────────────────────────────┐
│  STANDALONE AGENTS (profile: brain-agents)           │
│  3301 agent-hyper-brain-core  (full monolith clone)  │
│  3302 agent-mcp-bridge        (Ollama RAG bridge)    │
│  3303 agent-focus-tracker     (watchdog + sessions)  │
│  3304 agent-morning-briefing  (vault briefings)      │
└──────────────────────────────────────────────────────┘
         │
         │  NO connection (isolated)
         ▼
┌──────────────────────────────────────────────────────┐
│  AIFS LAYER (AI File System — standalone tools)      │
│  aifs_watcher.py     — FS enforcement daemon         │
│  aifs_mcp_server.py  — MCP contract server           │
│  AIFS/hub/           — Dashboard FastAPI (port 7331) │
│  AIFS/registry/      — Agent registry                │
└──────────────────────────────────────────────────────┘

scripts/  ← STALE MIRROR (dead — not imported anywhere)
```

---

## 🏆 Top 5 Nodes by Centrality (import fan-in/fan-out)

| Rank | Node | Centrality | Role |
|---|---|---|---|
| 1 | `hyper_brain_core.py` | 10 | Monolith orchestrator — imports everything |
| 2 | `analytics_engine.py` | 2 | Streak tracking, XP awards, heatmaps |
| 3 | `mcp_bridge.py` | 2 | Ollama RAG — used by core AND briefing |
| 4 | `focus_tracker.py` | 2 | Sessions + watchdog — used by core AND as agent |
| 5 | `morning_briefing_ai.py` | 2 | Vault briefings — used by core AND as agent |

---

## 🚨 Issues Found

### HIGH — Bugs that affect live behaviour

#### 1. `agent-morning-briefing` AI suggestions always null
**File:** `.agents/morning-briefing/morning_briefing_ai.py:401`

```python
_briefing = MorningBriefingAI(
    vault_path=os.environ.get("OBSIDIAN_VAULT_PATH", "/vault"),
    # mcp_bridge NOT passed — defaults to None
)
```

When `self.mcp is None`, `_get_ai_prioritization()` returns `None`, so every briefing
has `ai_suggestions: null` and `top_3` never uses AI reasoning.

**Fix:** Wire `agent-mcp-bridge` (port 3302) via HTTP instead of direct Python import:

```python
# In morning_briefing_ai.py __main__ block:
import httpx
class RemoteMCPBridge:
    connected = True
    async def query_vault(self, query, **kw):
        async with httpx.AsyncClient(timeout=10.0) as c:
            r = await c.post(f"{MCP_URL}/tools/call_mcp_tool", params={"query": query})
            return r.json()

_briefing = MorningBriefingAI(
    vault_path=os.environ.get("OBSIDIAN_VAULT_PATH", "/vault"),
    mcp_bridge=RemoteMCPBridge(),
)
```

#### 2. `asyncio.create_task()` called from watchdog thread
**File:** `focus_tracker.py:62`

```python
class VaultEventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        # ❌ watchdog runs this in a thread, not the event loop
        asyncio.create_task(self.tracker.record_activity(...))
```

This will raise `RuntimeError: no running event loop` silently.

**Fix:**
```python
def on_modified(self, event):
    loop = asyncio.get_event_loop()
    loop.call_soon_threadsafe(
        lambda: loop.create_task(self.tracker.record_activity(...))
    )
```

---

### MEDIUM — Code quality / stale state

#### 3. `constellation_builder.py` missing 6th repo
**File:** `constellation_builder.py:34`

```python
ECOSYSTEM_REPOS = [
    "HyperCode-V2.4", "HyperAgent-SDK", "Hyper-Vibe-Coding-Course",
    "BROskiPets-LLM-dNFT", "BROski-Obsidian-Brain",
    # ❌ "WelshDog-Mission-Control" missing — added 2026-05-xx
]
```

#### 4. `scripts/` is a stale mirror
`scripts/` contains 10 Python files that are word-for-word copies of the root-level scripts.
No Docker container, agent, or import references them. Safe to delete.

```
scripts/ai_distraction_filter.py    ← copy of ./ai_distraction_filter.py
scripts/analytics_engine.py         ← copy of ./analytics_engine.py
scripts/focus_tracker.py            ← copy of ./focus_tracker.py
scripts/hyper_brain_core.py         ← copy of ./hyper_brain_core.py
scripts/mcp_bridge.py               ← copy of ./mcp_bridge.py
scripts/morning_briefing_ai.py      ← copy of ./morning_briefing_ai.py
...
```

#### 5. AIFS layer is disconnected from brain agents
`AIFS/aifs_watcher.py` and `AIFS/aifs_mcp_server.py` are excellent tools but have
zero integration with the 4 brain agents. Contracts in `AIFS/` can't be enforced
against runtime agent writes to the vault.

---

### LOW — Minor issues

#### 6. `github_webhook_server.py` at root is orphaned
Webhook handling is already embedded in `hyper_brain_core.py` at `POST /webhook/github`.
The standalone `github_webhook_server.py` is never called.

#### 7. Zero tests for 3 core engine modules
`hyper_split.py`, `session_snapshot.py`, `ai_distraction_filter.py` — all imported
by `hyper_brain_core.py` — have no test coverage at all.

---

## 💡 Top 3 Upgrade Suggestions

### 1. Wire `agent-morning-briefing` → `agent-mcp-bridge` via HTTP
The briefing agent at :3304 never uses AI suggestions because `mcp_bridge=None`.
A thin HTTP adapter (see fix above) would unlock Ollama-powered daily prioritization
without changing the import structure of either module.
**Effort:** ~20 lines. **Impact:** High (turns on a whole feature branch).

### 2. Centralise streak-data reads into `analytics_engine`
`morning_briefing_ai.py:_get_streak_data()` and `analytics_engine.py:get_streaks()` both
open `07-Streaks-Achievements/streak-data.json` independently. Extract to a shared
`StreakStore` class (already exists as the read path in `analytics_engine`) — briefing
should call `analytics_engine.get_streaks()` rather than parsing the file itself.
**Effort:** ~10 lines. **Impact:** Removes data-drift risk.

### 3. AIFS contract enforcement in agent Dockerfiles
AIFS is built but idle. Add the watcher as a sidecar to `agent-hyper-brain-core`
(similar to `obsidian-sync.sh` WATCH_MODE pattern already live in V2.4):

```yaml
# docker-compose.brain.yml
agent-aifs-watcher:
  profiles: ["brain-agents"]
  build:
    context: ../BROski-Obsidian-Brain-for-HyperFocus-z0ne
    dockerfile: AIFS/Dockerfile
  command: ["python", "AIFS/aifs_watcher.py", "watch", "/vault", "--agent=brain-core"]
  volumes:
    - ${OBSIDIAN_VAULT_PATH}:/vault
```

**Effort:** ~1 Dockerfile + 8 compose lines. **Impact:** Activates AIFS (currently zero runtime value from a complete subsystem).

---

## 📁 Files by Layer

| File | Layer | Lines | Tests | Connected |
|---|---|---|---|---|
| `.agents/hyper-brain-core/hyper_brain_core.py` | agent | 432 | ✗ | ✓ |
| `.agents/mcp-bridge/mcp_bridge.py` | agent | 275 | ✗ | ✓ |
| `.agents/focus-tracker/focus_tracker.py` | agent | 383 | ✗ | ✓ |
| `.agents/morning-briefing/morning_briefing_ai.py` | agent | 434 | ✗ | partial |
| `analytics_engine.py` | engine | 280 | ✗ | ✓ |
| `constellation_builder.py` | engine | 149 | ✗ | ✓ |
| `difficulty_dial.py` | engine | ~80 | ✗ | ✓ |
| `events_feed.py` | engine | 31 | ✓ | ✓ |
| `gamification_summary.py` | engine | ~100 | ✓ | ✓ |
| `hyper_split.py` | engine | ? | ✗ | ✓ |
| `ai_distraction_filter.py` | engine | ? | ✗ | ✓ |
| `session_snapshot.py` | engine | ? | ✗ | ✓ |
| `github_webhook_server.py` | root | ? | ✗ | ✗ (orphan) |
| `AIFS/aifs_watcher.py` | aifs | 530 | ✗ | ✗ (disconnected) |
| `AIFS/aifs_mcp_server.py` | aifs | 551 | ✗ | ✗ (disconnected) |
| `AIFS/hub/aifs_hub_server.py` | aifs | ~200 | ✗ | ✗ (disconnected) |
| `scripts/*.py` | dead | ~1200 | ✗ | ✗ (stale mirror) |

---

## 🧹 Safe to Delete

- `scripts/` (entire directory — stale mirrors, 0 dependants)
- `github_webhook_server.py` at root (orphaned, logic already in core)

---

*Report by brain-graph-analysis · BROski♾️*
