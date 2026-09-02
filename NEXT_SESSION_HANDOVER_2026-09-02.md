# NEXT_SESSION_HANDOVER 2026-09-02

## 🔴 Blockers

None.

## 🟡 Pending — `agent-mcp-bridge` container is HOTPATCHED, not rebuilt

Graph Brain v5 (native communities + PageRank; branch `graph-brain-v5-communities`
merged to `main` as `b7bed40`, pushed to origin) is **live** on `agent-mcp-bridge`
(:3302) — but only via a hot-patch, not a real image build.

**What was done (2026-09-02 ~22:30):**

```
docker cp .agents/mcp-bridge/mcp_bridge.py agent-mcp-bridge:/app/mcp_bridge.py
docker restart agent-mcp-bridge
```

Rebuild was skipped on purpose: WSL RAM was at ~150 MB free / swap 83% used, and
the ecosystem rule is **never build while the stack is up** (8 GB ceiling).

**Consequence:** the running container's `/app/mcp_bridge.py` no longer matches
its image. Any recreate — `docker compose up`, `docker compose down && up`, a host
reboot, a Docker Desktop restart — reverts it to the June image (no
community-aware scoring, no `/graph/related` `related_by_community`).

**To make it permanent** (run when the stack is down OR RAM is free):

```
docker compose -f docker-compose.hyper-brain.yml build agent-mcp-bridge
docker compose -f docker-compose.hyper-brain.yml up -d agent-mcp-bridge
```

`.agents/mcp-bridge/Dockerfile` is `COPY . .` + `CMD ["python","mcp_bridge.py"]`,
so a plain build picks up the merged source. No other brain agent changed.

**Verify after rebuild** (all should already pass on the hot-patched container):

```
curl -s http://127.0.0.1:3302/graph | python -c "import sys,json;m=json.load(sys.stdin)['meta'];print(m['version'],m.get('communities_count'),m.get('community_algo'))"
# -> 5 116 greedy-modularity
curl -s "http://127.0.0.1:3302/graph/related/difficulty_dial?limit=4" | python -m json.tool
# -> response includes non-empty "related_by_community"
curl -s "http://127.0.0.1:3302/route?query=focus&limit=3" | python -c "import sys,json;print(sorted(json.load(sys.stdin)))"
# -> ['code', 'notes', 'query', 'seeds', 'skills']   (5-key shape unchanged)
```

## 🟢 Completed 2026-09-02

- Graph Brain v5 shipped end-to-end via full SDD run (spec → plan → 7 tasks →
  whole-branch review + 1 fix wave). 65 tests (from 32). Merged `b7bed40`, pushed.
- `communities.py` (new, stdlib): deterministic greedy-modularity communities +
  PageRank. `graph_builder.py` stamps `community` / `community_label` /
  `centrality_global`, `meta.version` 5, fail-open. `mcp_bridge.py`
  `related_nodes()` + `route_skills()` community-aware; new `community_members()`
  + `/graph/related` `related_by_community`.
- `graph.json` regenerated to v5 (topology byte-preserved: 268 nodes / 482 edges).
- `.github/workflows/graph-refresh.yml` now stamps communities on every vault-note push.
- Deferred code follow-ups: `docs/superpowers/plans/2026-09-02-graph-brain-v5-FOLLOWUPS.md` (7 items).

## 📋 References

- [FOLLOWUPS](docs/superpowers/plans/2026-09-02-graph-brain-v5-FOLLOWUPS.md)
- [spec](docs/superpowers/specs/2026-09-02-graph-brain-v5-communities-design.md)
- [plan](docs/superpowers/plans/2026-09-02-graph-brain-v5-communities.md)
