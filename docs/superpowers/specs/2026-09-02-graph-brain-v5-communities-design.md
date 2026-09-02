# Graph Brain v5 — Native Communities + PageRank for Smarter Retrieval & Routing

> **Status:** design — awaiting review
> **Date:** 2026-09-02
> **Branch:** `graph-brain-v5-communities`
> **Author:** Lyndz + Claude (brainstorming session)

---

## 1. Problem

THE HYPER BRAIN's memory hub is the canonical graph at
`HYPERFOCUS_ZONE/06-AI-Context/graph.json` (v4: 268 nodes, 482 edges, layers
`code / notes / mentions / skills`). It is built by the stdlib-only
`graph_builder.py` — which runs identically on the Windows host, inside the
`agent-mcp-bridge` container, and in GitHub Actions — and served by
`.agents/mcp-bridge/mcp_bridge.py` for:

- `related_nodes()` — 2-hop decayed expansion over `wikilink | mentions |
  skill-link` edges, score `= hop_weight * (1 + centrality)`
- `route_skills()` — `/route`: deterministic skill routing consumed by V2.4
  `crew-orchestrator` on every `/execute`
- graph-aware RAG (`_build_context` → `graph_neighbors` → `related_nodes`)

Retrieval and routing only ever follow **explicit edges**. Two notes about the
same topic that nobody wikilinked, or a skill relevant to a code module with no
`skill-link` edge, are invisible to expansion. `centrality` is raw degree count,
so a node linked by many trivial notes outranks a genuine hub.

A stale `graphify-out/` knowledge graph exists (5,261 nodes, 329 communities)
but is a poor enrichment source: symbol-level node IDs that don't match
canonical IDs, ~70% vendored third-party plugin code, **zero `.md`/notes
coverage**, last built 2026-07-09 with an abandoned partial re-run. Folding it in
would move almost nothing and needs a token-costly re-run to ever refresh.

## 2. Goal

Give `related_nodes()` and `route_skills()` a **community signal** and a **real
centrality signal**, computed natively inside `graph_builder.py` with **stdlib
only, zero new dependencies, zero token cost**, recomputed on every build so it
never goes stale. The improvement is invisible to callers — response shapes are
unchanged; results are better ranked and fill the "should connect but isn't
linked" gap.

### Non-goals

- No LLM-inferred concept edges in this spec — deferred (§10).
- No constellation viz changes — the D3 page keeps working; colouring by
  community is a later increment.
- No new dependency, no external tool, no CI change beyond what
  `python graph_builder.py` already does.
- No change to the `code` layer curation, the edge set, or the
  `wikilink | mentions | skill-link` expansion filter.

## 3. Approach (chosen over two alternatives)

| Approach | Verdict |
|---|---|
| **A** — fresh scoped `graphify` run → `graph_enrichment.json` → merge | rejected: needs graphify tokens + a fiddly symbol→`note:` crosswalk that must re-run to refresh; graphify's scale/LLM machinery is mismatched to a 268-node graph |
| **B** — enrich from the *existing* `graphify-out/` subset | rejected: covers ~20 of 268 nodes, nothing for notes/skills, 2 months stale — throwaway-proof value only |
| **C** — communities + PageRank computed natively in `graph_builder.py` | **chosen**: exact coverage of the retrieval universe (notes + skills included), never stale, no ID crosswalk, keeps the stdlib/in-container/Actions contract, no deps, no tokens |

The one thing C cannot produce — graphify's LLM-*inferred* concept edges — is a
self-contained later increment (§10) that plugs in without C depending on it.

## 4. Architecture

Three isolated, independently testable units:

| Unit | Location | Input → Output | Depends on |
|---|---|---|---|
| `detect_communities()` | `communities.py` (new, repo root, stdlib) | `(nodes, edges)` → `{node_id: community_id}`, `{community_id: label}` | pure function |
| `pagerank()` | `communities.py` | `(nodes, edges)` → `{node_id: float}` | pure function |
| `_derive_labels()` | `communities.py` | `(communities, nodes)` → `{community_id: label}` | pure function |
| merge/stamp step | `graph_builder.py` `merge()` | stamps `community`, `community_label`, `centrality_global`; bumps meta to v5 | `communities.py` |
| scoring changes | `mcp_bridge.py` `related_nodes()`, `route_skills()`, `/graph/related` | reads new node fields, fails open when absent | `graph.json` only |

**Data flow.** `graph_builder.py` runs (unchanged trigger: host, container, or
the `graph-refresh.yml` push hook) → builds code+notes+mentions+skills layers as
today → **new final step**: run `detect_communities()` + `pagerank()` over the
assembled node/edge set → stamp fields onto every node → atomic write.
`mcp-bridge` loads `graph.json` (already mtime-cached) → `related_nodes()` and
`route_skills()` factor `community` + `centrality_global` into their scores.

**Why a separate `communities.py`.** `graph_builder.py` is already ~360 lines
across four layer builds. Community detection + PageRank is ~170 lines of graph
math with its own test surface; a sibling module keeps each file focused and
lets tests hit the algorithms without a full vault scan.

## 5. Algorithms (`communities.py`, stdlib only)

### 5.1 Edge view

Both algorithms operate on the **retrieval topology**: edges of type
`wikilink`, `mentions`, `skill-link` only, treated as **undirected**. Code-only
edge types (`import`, `call`, `http-call`, `same-file`, `data-overlap`,
`stale-mirror`, `DISCONNECTED`, `optional-call`) are excluded — they don't drive
RAG and would fuse unrelated notes through shared code. A node with no retrieval
edge → its own singleton community, and the minimum `centrality_global` in the
graph (all edge-isolated nodes converge to one equal floor value — see §5.3).

### 5.2 `detect_communities()` — deterministic greedy modularity agglomeration

Chosen over label propagation because the output is committed to git and
regenerated on every push; a non-deterministic partition would churn `graph.json`
diffs and thrash the bridge's mtime cache.

```
adj  = undirected adjacency over filtered edges
m    = number of filtered undirected edges
deg  = degree per node over filtered edges
community = { node_id: {node_id} for each node }        # start: every node alone
node_comm = { node_id: node_id }

repeat up to N times (N = node count, hard cap):
    best = None            # (delta_Q, key) ; key = (min(repA,repB), max(repA,repB))
    for each filtered edge (u, v) with node_comm[u] != node_comm[v]:
        # standard Clauset-Newman-Moore modularity gain for merging comm(u), comm(v);
        # exact arithmetic pinned in code and locked by the known-partition test (§8.1)
        dQ = 2 * ( e_uv / (2*m)  -  (a_u * a_v) / (2*m)**2 )
             # e_uv  = number of edges between the two communities
             # a_c   = sum of degrees (over filtered edges) of community c
        if dQ > 0:
            cand_key = (min(repA, repB), max(repA, repB))
            if best is None or dQ > best.dQ or (dQ == best.dQ and cand_key < best.key):
                best = (dQ, cand_key, commA, commB)
    if best is None: break
    merge best.commB into best.commA ; update node_comm, a_c, e_* incrementally

final community_id of each node = lexicographically smallest member node_id
return { node_id: community_id }, plus the member sets for labelling
```

- **Determinism:** candidate pairs come only from filtered edges, iterated in
  sorted `(u, v)` order; the tie-break `(min_rep, max_rep)` is a total order; no
  randomness, no dict-iteration-order dependence.
- **Stable IDs across runs:** `community` value = *smallest member node-id*
  (e.g. `"hyper_brain_core"`, `"note:00-Inbox/Dashboard"`), not a counter.
  Adding a node to a cluster does not renumber other clusters; a cluster's ID
  changes only if its smallest member changes.
- **Performance:** ~268 nodes / ~300 filtered edges → converges in < 300 merges,
  sub-second. `max_merges = node_count` cap + a wall-clock assertion in tests
  guard a pathological future graph.
- **Resolution:** plain modularity. A single `gamma` parameter (default `1.0`,
  multiplies the `(a_u * a_v)` null term) is the only tuning knob; used only if
  the real vault produces a degenerate one-blob / all-singletons partition
  (checked at implementation time — see §7).

### 5.3 `pagerank()` — `centrality_global`

```
undirected filtered graph, power iteration
d = 0.85, tol = 1e-6, max_iter = 100
rank init = 1 / N for every node
each iter:
    new[n] = (1 - d) / N
           + d * ( sum over neighbours m of n:  rank[m] / deg(m) )
           + d * (dangling_mass / N)       # deg-0 nodes' rank spread uniformly
    stop when sum(|new - rank|) < tol
```

- Deterministic: fixed init, sorted iteration, fixed constants.
- Stored as `centrality_global` (float, observed range ~`0.0005`–`0.05`),
  rounded to 6 dp for a stable JSON diff.
- Existing `centrality` field is **left untouched** (degree / hand-set) — the
  constellation viz and `/graph/node` continue unchanged.
- On non-convergence in 100 iters: return the last iteration's values (still a
  usable ranking); a test asserts convergence on the real graph snapshot.

### 5.4 `_derive_labels()` — provisional, no LLM

Per community, first rule that applies:

1. **Common vault path segment** among `note:` members — if ≥ 60% share a path
   prefix segment (e.g. `02-Areas/Focus-Analytics/`), label = that segment
   (`"Focus-Analytics"`).
2. Else **dominant `category`** among `skill:` members (from the registry entry
   already on skill nodes) → `"<category> skills"`.
3. Else **highest-`centrality_global` member's id** → `"<id> cluster"`.

Deterministic, honest, adequate — the label is cosmetic; only the `community`
ID drives scoring. A future `06-AI-Context/community_labels.json` override map is
a one-line extension point, **not built here**.

### 5.5 Stamp step in `graph_builder.py`

New final block in `merge()`, after `graph["nodes"]` / `graph["edges"]` are
assembled and before the `meta` block is finalised:

```python
try:
    from communities import detect_communities, pagerank, derive_labels
    comm, members = detect_communities(graph["nodes"], graph["edges"])
    labels = derive_labels(members, graph["nodes"])
    pr = pagerank(graph["nodes"], graph["edges"])
    for n in graph["nodes"]:
        cid = comm[n["id"]]
        n["community"] = cid
        n["community_label"] = labels[cid]
        n["centrality_global"] = round(pr[n["id"]], 6)
    meta["version"] = 5
    meta["layers"] = ["code", "notes", "mentions", "skills", "communities"]
    meta["communities_count"] = len(set(comm.values()))
    meta["community_algo"] = "greedy-modularity"
except Exception as exc:                       # same fail-open posture as skills layer
    print(f"communities: skipped ({exc})")
    meta["version"] = 4
```

`communities.py` never imports anything outside the stdlib. If it raises for any
reason, the graph is written **without** the three fields and stays `version: 4`;
the bridge then runs today's behaviour unchanged.

## 6. Bridge scoring changes (`.agents/mcp-bridge/mcp_bridge.py`)

Every new branch guards on `.get("community")` / `.get("centrality_global")`
being present. A v4 graph → all branches skipped → behaviour byte-identical to
today (proved by a test, §7).

### 6.1 New constants (near the RAG-budget block)

```python
GRAPH_COMMUNITY_BONUS       = float(os.environ.get("GRAPH_COMMUNITY_BONUS", "1.5"))
GRAPH_COMMUNITY_SEED_FLOOR  = float(os.environ.get("GRAPH_COMMUNITY_SEED_FLOOR", "1.0"))
GRAPH_COMMUNITY_SEED_MAX    = int(os.environ.get("GRAPH_COMMUNITY_SEED_MAX", "3"))
GRAPH_ROUTE_COMMUNITY_BONUS = float(os.environ.get("GRAPH_ROUTE_COMMUNITY_BONUS", "1.0"))
```

### 6.2 `related_nodes()`

**a. Centrality term prefers PageRank, normalised to "multiples of average".**
PageRank mean is `1/N`; multiplying by `N` puts an average node at `~1.0` and
hubs at `~5`–`13`, the same magnitude as the old degree term, so the existing
`weight` / `decay` tuning still holds.

```python
n_count = len(nodes)
def _cent(node):
    pr = node.get("centrality_global")
    if pr is not None:
        return pr * n_count
    return node.get("centrality") or 0        # legacy fallback
```

**b. Same-community bonus during edge expansion.**

```python
seed_comms = {nodes[s].get("community") for s in seeds if nodes[s].get("community")}
...
score = weight * (1 + _cent(nodes[nb]))
if nodes[nb].get("community") in seed_comms:
    score *= GRAPH_COMMUNITY_BONUS
```

**c. Community-seeded expansion — the gap-filler.** After the hop loop, if
result budget remains (`len(scored) < limit * 3`) and `seed_comms` is non-empty,
add unvisited nodes that share a seed community **with no edge path required**:

- virtual weight = `decay ** hops` (ranks strictly below any edge-connected hit)
- include only if `_cent(node) >= GRAPH_COMMUNITY_SEED_FLOOR` (at/above average
  importance — stops a large community flooding results)
- add at most `GRAPH_COMMUNITY_SEED_MAX`
- no community bonus applied (already a community match)
- iterate candidates in sorted `(-_cent, node_id)` order for determinism

**d. Deterministic tiebreak** (fixes latent non-determinism in the current
code):

```python
ranked = sorted(scored.items(), key=lambda kv: (-kv[1], kv[0]))
```

### 6.3 `route_skills()`

After `seeds` (top token matches) is computed, collect their communities; in the
skill-ranking loop add a flat bonus to same-community skills:

```python
seed_comms = {n.get("community") for n in seeds if n.get("community")}
...
if skill_meta[nid].get("community") in seed_comms:
    skill_rank[nid] += GRAPH_ROUTE_COMMUNITY_BONUS
```

A task matching `focus_tracker` now surfaces focus-community skills even with no
`skill-link` edge. `related_nodes()`'s own community-seeding already helps here;
this sharpens the final rank.

### 6.4 `/graph/related/{node_id}` — transparency

Add a `related_by_community` field: node IDs sharing the target's `community`,
top by `centrality_global`, excluding anything already in
`related_paths` / `related_code` / `related_skills`. ~6 lines, uses the
already-loaded graph. Makes "why is this surfaced" visible.

### 6.5 Untouched

`_build_context()` still calls `graph_neighbors()` → `related_nodes()`, so RAG
picks up the improvement for free. Embeddings path, `/seeds`, `/route` response
shape, `crew-orchestrator` contract, `/graph`, `/graph/node` — all unchanged.

## 7. Schema, compatibility, error handling

### 7.1 Node — three new optional fields

```json
{ "id": "...", "layer": "...", "centrality": 10, "status": "live",
  "community": "hyper_brain_core",
  "community_label": "Hyper Brain Core",
  "centrality_global": 0.041827 }
```

Existing fields untouched. `centrality` stays as degree / hand-set.

### 7.2 Meta

`version: 5`; `layers` gains `"communities"`; new `communities_count`,
`community_algo: "greedy-modularity"`.

### 7.3 Edges

Unchanged. C adds none.

### 7.4 Consumer impact

| Consumer | Effect |
|---|---|
| `/graph`, `/graph/node` | extra fields in payload; ignored by readers that don't use them |
| `/graph/related` | better results + new `related_by_community` field |
| `/route` (incl. V2.4 `crew-orchestrator`) | shape `{skills,notes,code,seeds}` unchanged; better ranked |
| `constellation.html` + `test_constellation.py` | no change required; must stay green |
| `.github/workflows/graph-refresh.yml` | no change — still runs bare `python graph_builder.py` |
| old bridge ↔ v5 graph | fine — ignores unknown fields |
| new bridge ↔ v4 graph | fine — fail-open, today's behaviour |

### 7.5 Error handling

| Failure | Behaviour |
|---|---|
| `communities.py` raises during build | caught in `merge()`; graph written without new fields, stays `version: 4`; log `communities: skipped (<err>)` |
| degenerate partition (one blob / all singletons) on real vault | `gamma` knob (default 1.0); resolved at implementation time against the real graph |
| PageRank non-convergence in 100 iters | return last iteration's values; test asserts convergence on the real snapshot |
| bridge sees partial fields | each term guarded independently; a missing field disables only that term |
| pathological future graph | `max_merges = node_count` cap + wall-clock assertion in tests |

## 8. Testing

### 8.1 `tests/test_communities.py` — algorithms in isolation, no vault scan

- known 2-clique-bridge graph → expected 2-community partition
- **determinism**: build twice from identical input → identical `{node:community}`
  and identical PageRank dict
- **stable IDs**: add one node to a cluster → other clusters' `community`
  values unchanged
- isolated node → singleton community; its `centrality_global` equals the
  graph minimum and every edge-isolated node shares that exact value
- PageRank: star graph → centre ranks highest; values sum ≈ 1.0; converges
  < 100 iters
- label derivation: community of `note:02-Areas/Focus-Analytics/*` members →
  label `"Focus-Analytics"`; skill-only community → `"<category> skills"`
- wall-clock guard: 500-node random graph completes < 5 s

### 8.2 `tests/test_graph_builder_communities.py` — integration

- run `graph_builder.py` against a tiny fixture vault → `graph.json` has v5 meta
  and every node carries the three fields
- monkeypatch `communities` import to raise → graph still written, `version: 4`,
  no new fields, exit 0

### 8.3 `tests/test_bridge_community_scoring.py`

- synthetic v5 graph: a note in the seed's community with **no edge path** →
  appears in `related_nodes()` output, ranked below edge-connected hits
- same graph with the three fields stripped (v4) → output identical to the
  pre-change baseline (fail-open proof)
- `route_skills()`: skill in seed community with no `skill-link` edge → its rank
  rises vs baseline
- `GRAPH_COMMUNITY_SEED_MAX=0` → community-seeding fully disabled

### 8.4 `tests/test_retrieval_regression.py` + `tests/fixtures/` — the "did it help" gate

- `tests/fixtures/graph_v5_snapshot.json` — a real `graph.json` built with this
  branch, checked in
- `tests/fixtures/retrieval_cases.json` — ~10 hand-picked
  `{query, expect_notes[], expect_skills[]}` from the real vault, including 3–4
  "should connect but isn't wikilinked" cases
- assert: precision@5 of the v5 path `>=` the v4 path on **every** case, and
  strictly greater on at least the hand-picked gap cases

### 8.5 Regression

`test_constellation.py`, `test_brain_levels_18_19.py`, `test_events_feed.py`,
`test_gamification_summary.py`, `test_aifs_claude_hook.py` stay green. Pre-merge:
full `pytest` + the CI command `python graph_builder.py` run locally.

## 9. Files touched

| File | Change | ~LOC |
|---|---|---|
| `communities.py` | **new** — `detect_communities()`, `pagerank()`, `derive_labels()` | ~170 |
| `graph_builder.py` | import + stamp block in `merge()`, meta bump, try/except | ~25 |
| `.agents/mcp-bridge/mcp_bridge.py` | constants, `_cent()`, community bonus + seeding in `related_nodes()`, bonus in `route_skills()`, `related_by_community` in `/graph/related` | ~55 |
| `tests/test_communities.py` | new | ~140 |
| `tests/test_graph_builder_communities.py` | new | ~60 |
| `tests/test_bridge_community_scoring.py` | new | ~90 |
| `tests/test_retrieval_regression.py` | new | ~50 |
| `tests/fixtures/graph_v5_snapshot.json`, `tests/fixtures/retrieval_cases.json` | new fixtures | — |
| `HYPERFOCUS_ZONE/06-AI-Context/graph.json` | regenerated to v5 by the build; committed | — |
| `CLAUDE.md` | "Graph Brain" section: v4 → v5, communities layer, new env knobs | ~10 |
| `.claude/skills/hyper-brain-modules/SKILL.md` | update if it names the schema version | ~5 |

Implementation on branch `graph-brain-v5-communities`, TDD per task, merged after
the full suite + `python graph_builder.py` pass.

## 10. Deferred increment — graphify LLM-inferred concept edges (NOT this spec)

Ships independently on top of C:

- `scripts/graph_enrich.py` (host / CI only, non-stdlib permitted): runs a
  **scoped** `graphify` pass — vault `*.md` + Brain `*.py` + skills registry,
  excluding `.obsidian/`, `node_modules/`, `brain-bundle*`, `openhuman-build/`,
  minified JS.
- Extract **only `INFERRED` concept edges**, confidence ≥ 0.7, dedup against
  existing `wikilink` / `mentions`; map endpoints to canonical IDs by source
  file; write `06-AI-Context/graph_inferred_edges.json`.
- `graph_builder.py` gains an **optional** merge (file absent = no-op, preserve
  contract) appending them as `{type: "inferred"}` edges.
- `mcp_bridge.py` adds `inferred` to the expansion edge allow-list at a **lower
  weight** than `wikilink`.
- Communities + centrality stay **native to C**; graphify is only ever the
  source of the inferred *edges*. No dependency from C on this increment.

## 11. Open questions to settle at implementation time

1. Does plain modularity (`gamma = 1.0`) produce a sensible partition on the real
   268-node graph, or is one blob / all singletons the result? (Determines
   whether `gamma` needs a non-default value.)
2. Actual observed `centrality_global` range on the real graph — confirms the
   `pr * n_count` normalisation lands in the intended `~1.0` average band.
3. Final `retrieval_cases.json` set — chosen against the real vault during
   implementation with Lyndz's input on which "should-connect" pairs matter.
