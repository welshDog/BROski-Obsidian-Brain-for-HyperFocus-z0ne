# Graph Brain v5 — Native Communities + PageRank Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Compute Louvain-style communities and PageRank inside the stdlib-only `graph_builder.py` and teach `mcp_bridge` retrieval + skill routing to use them, so the memory hub surfaces topically-related notes/skills that have no explicit edge — with zero new dependencies and zero token cost.

**Architecture:** A new stdlib module `communities.py` (repo root) exposes three pure functions — `pagerank()`, `detect_communities()`, `derive_labels()`. `graph_builder.py`'s `merge()` gains a final fail-open step that stamps `community`, `community_label`, `centrality_global` onto every node and bumps `meta.version` to 5. `.agents/mcp-bridge/mcp_bridge.py`'s `related_nodes()` and `route_skills()` read those fields (fail-open on a v4 graph) to add a same-community score bonus, a bounded community-seeded expansion for edge-less matches, and a real centrality term.

**Tech Stack:** Python 3.9+ stdlib only for `communities.py` and the `graph_builder.py` step (CI runs bare `python graph_builder.py` on 3.12; host is 3.13; container is the `Dockerfile.hyper-brain` image). Tests: `pytest==8.2.2`. The bridge already depends on `aiohttp==3.14.1` (runtime `requirements.txt`).

**Spec:** `docs/superpowers/specs/2026-09-02-graph-brain-v5-communities-design.md` — read it alongside this plan.

## Global Constraints

- **`communities.py` and the `graph_builder.py` step: stdlib only.** No import outside the Python standard library. CI does not `pip install` before running `python graph_builder.py`.
- **Deterministic output.** `graph.json` is committed to git and regenerated on every vault push. Identical input → byte-identical `community` / `community_label` / `centrality_global` values. No reliance on `dict`/`set` iteration order; `str` hashing is randomised by default, so every iteration over a set/dict of node-ids that feeds a float sum or a selection MUST be `sorted()`.
- **Fail-open, both sides.** If `communities.py` is missing or raises, `graph_builder.py` writes the graph without the three fields and leaves `meta.version` at `4`. If the bridge loads a graph with no `community` / `centrality_global`, every v5 branch is skipped and behaviour is byte-identical to the pre-v5 ranker.
- **Untouched:** the `centrality` field (degree / hand-set), the edge set, the `wikilink | mentions | skill-link` expansion filter, response shapes of `/graph`, `/graph/node`, `/route`, the constellation page, and the `graph-refresh.yml` CI command.
- **Retrieval topology** for both algorithms = edges of type `wikilink`, `mentions`, `skill-link` only, undirected. All other edge types are ignored.
- **New env knobs (defaults):** `GRAPH_COMMUNITY_BONUS=1.5`, `GRAPH_COMMUNITY_SEED_FLOOR=1.0`, `GRAPH_COMMUNITY_SEED_MAX=3`, `GRAPH_ROUTE_COMMUNITY_BONUS=1.0`.
- **Atomic write** in `graph_builder.py` (`tempfile.mkstemp` + `os.replace`) is already in place — do not remove it.
- **Commits:** conventional-commit subject lines; end every commit body with
  `Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>` and
  `Claude-Session: https://claude.ai/code/session_012RjkCXg6AFBdQaUbtoW6Nf`.
- **Branch:** `graph-brain-v5-communities` (already created off `main`; the spec commit `5c96ffc` is on it).

---

## File Structure

| File | New/Mod | Responsibility |
|---|---|---|
| `communities.py` | **new** (repo root) | `_adjacency()`, `_mode()`, `pagerank()`, `detect_communities()`, `derive_labels()` — pure stdlib graph math, no I/O |
| `graph_builder.py` | modify (`merge()`, end of function) | fail-open stamp step: call the three functions, write `community` / `community_label` / `centrality_global`, bump `meta` |
| `.agents/mcp-bridge/mcp_bridge.py` | modify | 4 module constants; `related_nodes()` — `_cent()`, community bonus, community-seeded expansion, deterministic tiebreak; `route_skills()` — community route bonus; `/graph/related` — `related_by_community` field |
| `tests/test_communities.py` | **new** | unit tests for all of `communities.py`, no vault scan |
| `tests/test_graph_builder_communities.py` | **new** | integration: run `graph_builder.py` against a fixture vault; fail-open path |
| `tests/test_bridge_community_scoring.py` | **new** | `related_nodes()` / `route_skills()` behaviour on a synthetic v5 graph + v4 fail-open parity |
| `tests/test_retrieval_regression.py` | **new** | precision@5 gate: v5 ≥ v4 on real-vault fixture cases |
| `tests/fixtures/graph_v5_snapshot.json` | **new** | real `graph.json` built on this branch (generated in Task 6) |
| `tests/fixtures/retrieval_cases.json` | **new** | ~10 hand-labelled `{query, expect_notes, expect_skills}` cases |
| `tests/fixtures/mini_vault/` | **new** | 4-note fixture vault + seed `graph.json` for Task 3 |
| `requirements-dev.txt` | modify (maybe) | add `aiohttp==3.14.1` if `import mcp_bridge` fails in the dev env |
| `CLAUDE.md` | modify | "Graph Brain" section: v4 → v5, communities layer, env knobs |
| `HYPERFOCUS_ZONE/06-AI-Context/graph.json` | regenerate | v5 output, committed |

`Dockerfile.hyper-brain` needs **no change** — line 25 `COPY *.py ./` already copies `communities.py` into the image next to `mcp_bridge.py` and `graph_builder.py`.

---

## Task 0: Pre-flight

**Files:** none (verification only)

- [ ] **Step 1: Confirm branch and baseline**

Run:
```bash
cd "H:/HYPERFOCUSZONE/HperCore/BROski-Obsidian-Brain-for-HyperFocus-z0ne"
git branch --show-current        # expect: graph-brain-v5-communities
git status --porcelain           # expect: only " M HYPERFOCUS_ZONE/06-AI-Context/graph.json" (pre-existing, unrelated)
```

- [ ] **Step 2: Record the pre-existing graph.json modification**

There is an uncommitted change to `HYPERFOCUS_ZONE/06-AI-Context/graph.json` on this branch that predates this work. Task 6/7 regenerate this file wholesale. Before committing the regenerated file in Task 7, show Lyndz `git diff HYPERFOCUS_ZONE/06-AI-Context/graph.json` and confirm the pre-existing change is either captured by the regen or intentionally discarded. Do not `git checkout` or stash it now.

- [ ] **Step 3: Baseline test run**

Run:
```bash
python -m pytest tests/ -q
```
Expected: all existing tests pass (`test_aifs_claude_hook`, `test_brain_levels_18_19`, `test_constellation`, `test_events_feed`, `test_gamification_summary`). Record the count. If any already fail, stop and report — do not build on a red baseline.

- [ ] **Step 4: Confirm the bridge imports in the dev env**

Run:
```bash
python -c "import sys, os; sys.path.insert(0, os.path.join('.agents','mcp-bridge')); import mcp_bridge; print('ok', mcp_bridge.OLLAMA_MODEL)"
```
Expected: `ok mistral`. If it fails with `ModuleNotFoundError: No module named 'aiohttp'`, add `aiohttp==3.14.1` to `requirements-dev.txt`, run `pip install -r requirements-dev.txt`, retry. Commit that one-line dev-deps change if made:
```bash
git add requirements-dev.txt && git commit -m "chore(dev): add aiohttp to dev deps for bridge unit tests

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_012RjkCXg6AFBdQaUbtoW6Nf"
```

---

## Task 1: `communities.py` — `pagerank()` + shared helpers

**Files:**
- Create: `communities.py`
- Test: `tests/test_communities.py`

**Interfaces:**
- Consumes: nothing (pure stdlib)
- Produces:
  - `FILTERED_EDGE_TYPES = ("wikilink", "mentions", "skill-link")`
  - `_adjacency(nodes: list[dict], edges: list[dict]) -> dict[str, set[str]]` — undirected adjacency over filtered edges; every node id from `nodes` is a key (isolated nodes map to an empty set); self-loops and edges to unknown ids dropped.
  - `pagerank(nodes: list[dict], edges: list[dict], damping: float = 0.85, tol: float = 1e-6, max_iter: int = 100) -> dict[str, float]` — deterministic undirected PageRank over `_adjacency`; returns a score per node id; `{}` if `nodes` is empty.

- [ ] **Step 1: Write the failing test**

Create `tests/test_communities.py`:
```python
"""Unit tests for communities.py — pure graph math, no vault scan."""
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from communities import _adjacency, pagerank  # noqa: E402


def _n(*ids):
    return [{"id": i, "layer": "note"} for i in ids]


def _e(*pairs, type="wikilink"):
    return [{"from": a, "to": b, "type": type} for a, b in pairs]


def test_adjacency_ignores_non_retrieval_edges():
    nodes = _n("a", "b", "c")
    edges = _e(("a", "b")) + [{"from": "b", "to": "c", "type": "import"}]
    adj = _adjacency(nodes, edges)
    assert adj["a"] == {"b"}
    assert adj["b"] == {"a"}
    assert adj["c"] == set()          # 'import' edge ignored


def test_adjacency_drops_self_loops_and_unknown_ids():
    nodes = _n("a", "b")
    edges = _e(("a", "a"), ("a", "zzz"), ("a", "b"))
    adj = _adjacency(nodes, edges)
    assert adj["a"] == {"b"}


def test_pagerank_star_centre_ranks_highest():
    nodes = _n("hub", "l1", "l2", "l3", "l4")
    edges = _e(("hub", "l1"), ("hub", "l2"), ("hub", "l3"), ("hub", "l4"))
    pr = pagerank(nodes, edges)
    assert pr["hub"] == max(pr.values())
    assert abs(sum(pr.values()) - 1.0) < 1e-6


def test_pagerank_is_deterministic_across_runs():
    nodes = _n("a", "b", "c", "d", "e", "f")
    edges = _e(("a", "b"), ("b", "c"), ("c", "a"), ("d", "e"), ("e", "f"), ("c", "d"))
    assert pagerank(nodes, edges) == pagerank(nodes, edges)


def test_pagerank_isolated_nodes_share_one_floor_value():
    nodes = _n("a", "b", "iso1", "iso2")
    edges = _e(("a", "b"))
    pr = pagerank(nodes, edges)
    assert pr["iso1"] == pr["iso2"]
    assert pr["iso1"] == min(pr.values())


def test_pagerank_empty_graph():
    assert pagerank([], []) == {}


def test_pagerank_converges_quickly_on_medium_graph():
    nodes = _n(*[f"x{i}" for i in range(120)])
    edges = _e(*[(f"x{i}", f"x{(i * 7 + 3) % 120}") for i in range(120)])
    start = time.time()
    pr = pagerank(nodes, edges)
    assert time.time() - start < 2.0
    assert abs(sum(pr.values()) - 1.0) < 1e-4
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest tests/test_communities.py -q`
Expected: `ModuleNotFoundError: No module named 'communities'` (collection error).

- [ ] **Step 3: Write `communities.py` with the helpers + `pagerank()`**

Create `communities.py`:
```python
#!/usr/bin/env python3
"""
communities.py
THE HYPER BRAIN — Graph Memory Hub v5

Pure stdlib graph math for the canonical memory-hub artifact
(HYPERFOCUS_ZONE/06-AI-Context/graph.json):

  pagerank()          -> centrality_global per node
  detect_communities() -> deterministic greedy-modularity partition
  derive_labels()     -> provisional community labels, no LLM

Runs identically on the Windows host, inside the agent-mcp-bridge container,
and in GitHub Actions. Deterministic: identical input -> identical output,
independent of dict/set iteration order.

BROski♾️
"""

# Retrieval topology: the only edge types RAG expansion follows.
FILTERED_EDGE_TYPES = ("wikilink", "mentions", "skill-link")


def _adjacency(nodes, edges):
    """Undirected adjacency over FILTERED_EDGE_TYPES only.
    Every node id is a key; isolated nodes map to an empty set. Self-loops and
    endpoints not present in `nodes` are dropped."""
    ids = {n["id"] for n in nodes}
    adj = {nid: set() for nid in ids}
    for e in edges:
        if e.get("type") not in FILTERED_EDGE_TYPES:
            continue
        a, b = e.get("from"), e.get("to")
        if a in ids and b in ids and a != b:
            adj[a].add(b)
            adj[b].add(a)
    return adj


def _mode(seq):
    """Most common value in `seq`; ties broken by sorted value. Deterministic.
    Returns (value, count) or (None, 0) for an empty sequence."""
    counts = {}
    for x in seq:
        counts[x] = counts.get(x, 0) + 1
    best_x, best_c = None, 0
    for x in sorted(counts):
        if counts[x] > best_c:
            best_x, best_c = x, counts[x]
    return best_x, best_c


def pagerank(nodes, edges, damping=0.85, tol=1.0e-6, max_iter=100):
    """Deterministic undirected PageRank over the filtered adjacency.

    Returns {node_id: score}. Dangling (edge-isolated) nodes converge to one
    shared floor value. Iteration over neighbours is sorted so float addition
    order — and therefore the 6-dp-rounded result — is stable run to run.
    """
    adj = _adjacency(nodes, edges)
    ids = sorted(adj)
    n = len(ids)
    if n == 0:
        return {}
    rank = {nid: 1.0 / n for nid in ids}
    deg = {nid: len(adj[nid]) for nid in ids}
    for _ in range(max_iter):
        dangling = damping * sum(rank[nid] for nid in ids if deg[nid] == 0) / n
        base = (1.0 - damping) / n + dangling
        new = {nid: base for nid in ids}
        for nid in ids:
            d = deg[nid]
            if d == 0:
                continue
            share = damping * rank[nid] / d
            for nb in sorted(adj[nid]):
                new[nb] += share
        delta = sum(abs(new[nid] - rank[nid]) for nid in ids)
        rank = new
        if delta < tol:
            break
    return rank
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest tests/test_communities.py -q`
Expected: 7 passed.

- [ ] **Step 5: Commit**

```bash
git add communities.py tests/test_communities.py
git commit -m "feat(graph): communities.py — deterministic PageRank + adjacency helpers

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_012RjkCXg6AFBdQaUbtoW6Nf"
```

---

## Task 2: `communities.py` — `detect_communities()` + `derive_labels()`

**Files:**
- Modify: `communities.py` (append two functions)
- Test: `tests/test_communities.py` (append)

**Interfaces:**
- Consumes: `_adjacency`, `_mode` from Task 1
- Produces:
  - `detect_communities(nodes: list[dict], edges: list[dict], gamma: float = 1.0) -> tuple[dict[str, str], dict[str, list[str]]]` — returns `(node_community, members)`. `node_community[node_id]` is the community id; `members[community_id]` is the sorted list of member ids. **The community id is the lexicographically smallest member node-id.** Every node id from `nodes` appears exactly once. Deterministic.
  - `derive_labels(members: dict[str, list[str]], nodes: list[dict], pagerank: dict[str, float]) -> dict[str, str]` — one label per community id. Rule order: (1) common first path-segment among `note:` members if ≥60% share it; (2) `"<dominant skill category> skills"` if the community has `skill` nodes with a `category`; (3) `"<highest-centrality_global member id> cluster"`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_communities.py`:
```python
from communities import detect_communities, derive_labels  # noqa: E402


def test_detect_two_cliques_joined_by_one_bridge():
    nodes = _n("a1", "a2", "a3", "b1", "b2", "b3")
    edges = _e(("a1", "a2"), ("a2", "a3"), ("a3", "a1"),
               ("b1", "b2"), ("b2", "b3"), ("b3", "b1"),
               ("a1", "b1"))                       # single bridge
    node_comm, members = detect_communities(nodes, edges)
    assert node_comm["a1"] == node_comm["a2"] == node_comm["a3"]
    assert node_comm["b1"] == node_comm["b2"] == node_comm["b3"]
    assert node_comm["a1"] != node_comm["b1"]
    assert node_comm["a1"] == "a1"                 # id == smallest member
    assert members["a1"] == ["a1", "a2", "a3"]


def test_detect_is_deterministic():
    nodes = _n(*[f"z{i:02d}" for i in range(20)])
    edges = _e(*[(f"z{i:02d}", f"z{(i + 1) % 20:02d}") for i in range(20)],
               *[(f"z{i:02d}", f"z{(i + 2) % 20:02d}") for i in range(0, 20, 4)])
    assert detect_communities(nodes, edges)[0] == detect_communities(nodes, edges)[0]


def test_detect_stable_ids_when_a_node_is_added():
    base_nodes = _n("a1", "a2", "a3", "b1", "b2", "b3")
    base_edges = _e(("a1", "a2"), ("a2", "a3"), ("a3", "a1"),
                    ("b1", "b2"), ("b2", "b3"), ("b3", "b1"), ("a1", "b1"))
    comm_before, _ = detect_communities(base_nodes, base_edges)
    # add a4 attached to the a-clique; b-clique ids must not renumber
    nodes2 = base_nodes + _n("a4")
    edges2 = base_edges + _e(("a4", "a2"), ("a4", "a3"))
    comm_after, _ = detect_communities(nodes2, edges2)
    assert comm_after["b1"] == comm_before["b1"]
    assert comm_after["a4"] == comm_after["a1"]


def test_detect_isolated_node_is_its_own_singleton():
    nodes = _n("a", "b", "iso")
    edges = _e(("a", "b"))
    node_comm, members = detect_communities(nodes, edges)
    assert node_comm["iso"] == "iso"
    assert members["iso"] == ["iso"]


def test_detect_no_edges_all_singletons():
    nodes = _n("a", "b", "c")
    node_comm, members = detect_communities(nodes, [])
    assert set(node_comm.values()) == {"a", "b", "c"}


def test_detect_wall_clock_guard_500_nodes():
    nodes = _n(*[f"n{i:03d}" for i in range(500)])
    edges = _e(*[(f"n{i:03d}", f"n{(i * 13 + 7) % 500:03d}") for i in range(500)])
    start = time.time()
    detect_communities(nodes, edges)
    assert time.time() - start < 5.0


def test_derive_labels_common_path_segment():
    members = {"note:02-Areas/Focus-Analytics/weekly": [
        "note:02-Areas/Focus-Analytics/weekly",
        "note:02-Areas/Focus-Analytics/heatmap",
        "note:02-Areas/Focus-Analytics/trends",
    ]}
    nodes = [{"id": i, "layer": "note", "path": i.split("note:")[1] + ".md"}
             for i in members["note:02-Areas/Focus-Analytics/weekly"]]
    labels = derive_labels(members, nodes, {})
    assert labels["note:02-Areas/Focus-Analytics/weekly"] == "02-Areas"


def test_derive_labels_skill_category_then_fallback():
    members = {"skill:HS-010": ["skill:HS-010", "skill:HS-011"], "x": ["x"]}
    nodes = [
        {"id": "skill:HS-010", "layer": "skill", "category": "focus"},
        {"id": "skill:HS-011", "layer": "skill", "category": "focus"},
        {"id": "x", "layer": "engine"},
    ]
    labels = derive_labels(members, nodes, {"x": 0.01})
    assert labels["skill:HS-010"] == "focus skills"
    assert labels["x"] == "x cluster"
```

- [ ] **Step 2: Run to verify they fail**

Run: `python -m pytest tests/test_communities.py -q`
Expected: `ImportError: cannot import name 'detect_communities'`.

- [ ] **Step 3: Append the implementation to `communities.py`**

```python
def detect_communities(nodes, edges, gamma=1.0):
    """Deterministic greedy-modularity (Clauset-Newman-Moore) agglomeration
    over the filtered adjacency.

    Returns (node_community, members):
      node_community[node_id] -> community id (== smallest member node-id)
      members[community_id]    -> sorted list of member node-ids

    No randomness; selection is an argmax over a total order, so dict/set
    iteration order cannot change the result.
    """
    adj = _adjacency(nodes, edges)
    ids = sorted(adj)

    edge_pairs = set()
    for nid in ids:
        for nb in adj[nid]:
            edge_pairs.add((nid, nb) if nid < nb else (nb, nid))
    m = len(edge_pairs)

    node_comm = {nid: nid for nid in ids}
    members = {nid: [nid] for nid in ids}
    if m == 0:
        return node_comm, members

    deg = {nid: len(adj[nid]) for nid in ids}
    a = {nid: float(deg[nid]) for nid in ids}      # sum of degrees per community
    two_m = 2.0 * m

    # cut map: edges between distinct communities, keyed (c_lo, c_hi)
    e_between = {}
    for u, v in sorted(edge_pairs):
        c1, c2 = node_comm[u], node_comm[v]
        key = (c1, c2) if c1 < c2 else (c2, c1)
        e_between[key] = e_between.get(key, 0.0) + 1.0

    for _ in range(len(ids)):                       # hard cap = node count
        best = None                                # (dQ, key, c_keep, c_drop)
        for (c1, c2), e_uv in e_between.items():
            if e_uv <= 0.0:
                continue
            dQ = 2.0 * (e_uv / two_m
                        - gamma * (a[c1] * a[c2]) / (two_m * two_m))
            if dQ <= 0.0:
                continue
            if best is None or dQ > best[0] or (dQ == best[0] and (c1, c2) < best[1]):
                best = (dQ, (c1, c2), c1, c2)
        if best is None:
            break
        _, _, ca, cb = best
        keep, drop = (ca, cb) if ca < cb else (cb, ca)

        members[keep].extend(members[drop])
        members[keep].sort()
        for nid in members[drop]:
            node_comm[nid] = keep
        del members[drop]
        a[keep] += a[drop]
        del a[drop]

        merged = {}
        for (x, y), w in e_between.items():
            nx = keep if x in (ca, cb) else x
            ny = keep if y in (ca, cb) else y
            if nx == ny:
                continue                           # now intra-community
            k = (nx, ny) if nx < ny else (ny, nx)
            merged[k] = merged.get(k, 0.0) + w
        e_between = merged

    return node_comm, members


def derive_labels(members, nodes, pagerank):
    """Provisional community labels, no LLM. Deterministic.

    1. common first path-segment among note: members (>= 60%)
    2. '<dominant skill category> skills'
    3. '<highest centrality_global member id> cluster'
    """
    by_id = {n["id"]: n for n in nodes}
    labels = {}
    for cid in sorted(members):
        mem = members[cid]

        segs = [by_id[nid]["path"].split("/")[0]
                for nid in mem
                if by_id.get(nid, {}).get("layer") == "note"
                and by_id[nid].get("path")]
        if segs:
            top_seg, count = _mode(segs)
            if count / len(segs) >= 0.6:
                labels[cid] = top_seg
                continue

        cats = [by_id[nid]["category"]
                for nid in mem
                if by_id.get(nid, {}).get("layer") == "skill"
                and by_id[nid].get("category")]
        if cats:
            labels[cid] = f"{_mode(cats)[0]} skills"
            continue

        top = max(sorted(mem), key=lambda nid: pagerank.get(nid, 0.0))
        labels[cid] = f"{top} cluster"
    return labels
```

- [ ] **Step 4: Run to verify they pass**

Run: `python -m pytest tests/test_communities.py -q`
Expected: 15 passed (7 from Task 1 + 8 here).

- [ ] **Step 5: Commit**

```bash
git add communities.py tests/test_communities.py
git commit -m "feat(graph): deterministic greedy-modularity communities + label derivation

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_012RjkCXg6AFBdQaUbtoW6Nf"
```

---

## Task 3: `graph_builder.py` stamp step + calibration

**Files:**
- Modify: `graph_builder.py` — inside `merge()`, immediately before `return graph` (currently line ~306)
- Create: `tests/fixtures/mini_vault/` (4 `.md` notes + a seed `graph.json`)
- Create: `tests/test_graph_builder_communities.py`

**Interfaces:**
- Consumes: `detect_communities`, `pagerank`, `derive_labels` from Tasks 1–2
- Produces: `graph.json` nodes carry `community` (str), `community_label` (str), `centrality_global` (float, 6 dp); `meta.version == 5`, `meta.layers` ends with `"communities"`, `meta.communities_count` (int), `meta.community_algo == "greedy-modularity"`. On any exception: fields absent, `meta.version == 4`, a `communities: skipped (...)` line on stdout, exit 0.

- [ ] **Step 1: Write the failing test + fixture vault**

Create `tests/fixtures/mini_vault/06-AI-Context/graph.json`:
```json
{
  "meta": {"version": 4, "layers": ["code", "notes", "mentions", "skills"]},
  "nodes": [
    {"id": "hyper_brain_core", "layer": "monolith", "centrality": 5, "status": "live"}
  ],
  "edges": [],
  "issues": []
}
```

Create `tests/fixtures/mini_vault/01-Projects/Alpha.md`:
```markdown
# Alpha
Links to [[Beta]] and mentions hyper_brain_core.
```
Create `tests/fixtures/mini_vault/01-Projects/Beta.md`:
```markdown
# Beta
Links back to [[Alpha]] and to [[Gamma]].
```
Create `tests/fixtures/mini_vault/02-Areas/Gamma.md`:
```markdown
# Gamma
Links to [[Beta]].
```
Create `tests/fixtures/mini_vault/02-Areas/Delta.md`:
```markdown
# Delta
An orphan note, no links.
```

Create `tests/test_graph_builder_communities.py`:
```python
"""Integration: graph_builder.py stamps v5 community fields, fail-open on error."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MINI = os.path.join(os.path.dirname(__file__), "fixtures", "mini_vault")


def _run_builder(vault, extra_env=None):
    env = dict(os.environ)
    env["BRAIN_SKILLS_PATH"] = os.path.join(vault, "_no_skills_here")  # force preserve-mode
    if extra_env:
        env.update(extra_env)
    proc = subprocess.run(
        [sys.executable, "graph_builder.py", "--vault", vault],
        cwd=REPO, env=env, capture_output=True, text=True,
    )
    return proc


def test_v5_fields_stamped_on_every_node():
    with tempfile.TemporaryDirectory() as tmp:
        vault = os.path.join(tmp, "HYPERFOCUS_ZONE")
        shutil.copytree(MINI, vault)
        proc = _run_builder(vault)
        assert proc.returncode == 0, proc.stderr
        graph = json.load(open(os.path.join(vault, "06-AI-Context", "graph.json"), encoding="utf-8"))
        assert graph["meta"]["version"] == 5
        assert graph["meta"]["layers"][-1] == "communities"
        assert graph["meta"]["community_algo"] == "greedy-modularity"
        assert isinstance(graph["meta"]["communities_count"], int)
        for n in graph["nodes"]:
            assert "community" in n
            assert "community_label" in n
            assert isinstance(n["centrality_global"], float)
        # Alpha<->Beta<->Gamma are one community; Delta is its own singleton
        by_id = {n["id"]: n for n in graph["nodes"]}
        assert by_id["note:Alpha"]["community"] == by_id["note:Beta"]["community"]
        assert by_id["note:Delta"]["community"] == "note:Delta"


def test_fail_open_when_communities_module_raises(monkeypatch):
    with tempfile.TemporaryDirectory() as tmp:
        vault = os.path.join(tmp, "HYPERFOCUS_ZONE")
        shutil.copytree(MINI, vault)
        # shadow communities.py with one that raises on import
        boom = os.path.join(tmp, "communities.py")
        open(boom, "w").write("raise RuntimeError('boom')\n")
        proc = _run_builder(vault, extra_env={"PYTHONPATH": tmp})
        assert proc.returncode == 0
        assert "communities: skipped" in proc.stdout
        graph = json.load(open(os.path.join(vault, "06-AI-Context", "graph.json"), encoding="utf-8"))
        assert graph["meta"]["version"] == 4
        assert all("community" not in n for n in graph["nodes"])
```

- [ ] **Step 2: Run to verify it fails**

Run: `python -m pytest tests/test_graph_builder_communities.py -q`
Expected: `test_v5_fields_stamped_on_every_node` FAILS (`assert graph["meta"]["version"] == 5` — it's still 4); `test_fail_open...` passes accidentally (already v4) — that's fine, it locks the behaviour.

- [ ] **Step 3: Add the stamp step to `graph_builder.py`**

In `merge()`, replace the final `return graph` with:
```python
    # ── v5: native communities + PageRank over the retrieval topology ──
    try:
        from communities import detect_communities, pagerank, derive_labels
        pr = pagerank(graph["nodes"], graph["edges"])
        node_comm, comm_members = detect_communities(graph["nodes"], graph["edges"])
        labels = derive_labels(comm_members, graph["nodes"], pr)
        for n in graph["nodes"]:
            cid = node_comm[n["id"]]
            n["community"] = cid
            n["community_label"] = labels[cid]
            n["centrality_global"] = round(pr.get(n["id"], 0.0), 6)
        meta["version"] = 5
        meta["layers"] = ["code", "notes", "mentions", "skills", "communities"]
        meta["communities_count"] = len(set(node_comm.values()))
        meta["community_algo"] = "greedy-modularity"
    except Exception as exc:  # fail-open — same posture as the skills-layer preserve path
        print(f"communities: skipped ({exc})")

    return graph
```

- [ ] **Step 4: Run to verify the tests pass**

Run: `python -m pytest tests/test_graph_builder_communities.py -q`
Expected: 2 passed.

- [ ] **Step 5: Calibration run against the REAL vault**

Run:
```bash
python graph_builder.py
python -c "import json; g=json.load(open('HYPERFOCUS_ZONE/06-AI-Context/graph.json', encoding='utf-8')); \
m=g['meta']; \
from collections import Counter; c=Counter(n['community'] for n in g['nodes']); \
print('version', m['version'], 'nodes', m['total_nodes'], 'communities', m['communities_count']); \
print('largest 5:', c.most_common(5)); \
print('singletons:', sum(1 for v in c.values() if v==1)); \
print('sample labels:', sorted({n['community_label'] for n in g['nodes']})[:12])"
```

Evaluate the output against the spec's open questions (§11):
- If `communities_count` is `1` (one giant blob) OR equals `total_nodes` (all singletons): the partition is degenerate. Add `gamma` handling to the `graph_builder.py` call — `detect_communities(..., gamma=float(os.environ.get("BRAIN_COMMUNITY_GAMMA", "1.0")))` — and try `gamma` in `{0.5, 2.0}` to find a value giving 8–40 communities with the largest under ~40% of nodes. Record the chosen value in the spec (§11 answer) and default it in code.
- If the partition looks reasonable (roughly: 10–40 communities, largest cluster < 40% of nodes, the 4 brain agents landing together, PARA folders roughly coherent): keep `gamma=1.0`, no code change.
- Record the observed `centrality_global` range: `python -c "import json; g=json.load(open('HYPERFOCUS_ZONE/06-AI-Context/graph.json', encoding='utf-8')); v=[n['centrality_global'] for n in g['nodes']]; print(min(v), max(v), sum(v)/len(v))"`. Confirm `max/avg` is roughly 5–15 (so `pr * n_count` normalisation in Task 4 lands an average node near 1.0). If wildly off, note it for Task 4's `_cent` — but do not change Task 4's formula without discussing with Lyndz.

- [ ] **Step 6: Restore the working-tree graph.json for now**

The real regenerate + commit happens in Task 7 after the bridge changes land. For now:
```bash
git checkout HYPERFOCUS_ZONE/06-AI-Context/graph.json   # discard the calibration regen
```
(The pre-existing unrelated modification from Task 0 Step 2 is restored by this too — that's intended; it's revisited in Task 7.)

- [ ] **Step 7: Commit**

```bash
git add graph_builder.py tests/test_graph_builder_communities.py tests/fixtures/mini_vault
# plus graph_builder.py gamma change ONLY if calibration required it
git commit -m "feat(graph): stamp v5 communities + centrality_global in graph_builder merge()

Fail-open: missing/raising communities.py leaves the graph at v4.
Calibration: gamma=<VALUE FROM STEP 5>.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_012RjkCXg6AFBdQaUbtoW6Nf"
```

---

## Task 4: `mcp_bridge.py` — `related_nodes()` community-aware scoring

**Files:**
- Modify: `.agents/mcp-bridge/mcp_bridge.py` — module constants (after line ~36) and `related_nodes()` (lines ~187–221)
- Test: `tests/test_bridge_community_scoring.py`

**Interfaces:**
- Consumes: v5 `graph.json` node fields `community`, `centrality_global`
- Produces: `related_nodes()` unchanged signature `(seed_ids, limit=5, hops=2, decay=0.4) -> list[dict]`; on a v5 graph it applies `GRAPH_COMMUNITY_BONUS`, community-seeded expansion (≤ `GRAPH_COMMUNITY_SEED_MAX`, gated by `GRAPH_COMMUNITY_SEED_FLOOR`), and a PageRank-based centrality term; on a v4 graph output is identical to the pre-change ranker.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_bridge_community_scoring.py`:
```python
"""related_nodes() / route_skills() community-aware scoring, + v4 fail-open parity."""
import json
import os
import sys

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", ".agents", "mcp-bridge")))

import mcp_bridge  # noqa: E402


def _bridge(tmp_path, graph):
    vault = tmp_path / "vault"
    (vault / "06-AI-Context").mkdir(parents=True)
    (vault / "06-AI-Context" / "graph.json").write_text(json.dumps(graph), encoding="utf-8")
    return mcp_bridge.MCPBridge(vault_path=str(vault))


# seed 's' is edge-linked to 'edge_hit'. 'comm_hit' shares s's community but has
# NO edge path. 'far' is in neither.
_V5 = {
    "meta": {"version": 5},
    "nodes": [
        {"id": "s",        "layer": "note", "path": "s.md",        "community": "s", "centrality_global": 0.02},
        {"id": "edge_hit", "layer": "note", "path": "edge_hit.md", "community": "s", "centrality_global": 0.03},
        {"id": "comm_hit", "layer": "note", "path": "comm_hit.md", "community": "s", "centrality_global": 0.05},
        {"id": "far",      "layer": "note", "path": "far.md",      "community": "far", "centrality_global": 0.09},
    ],
    "edges": [{"from": "s", "to": "edge_hit", "type": "wikilink"}],
    "issues": [],
}


def _v4(graph):
    g = json.loads(json.dumps(graph))
    g["meta"]["version"] = 4
    for n in g["nodes"]:
        n.pop("community", None)
        n.pop("centrality_global", None)
    return g


def test_community_only_node_is_surfaced_with_no_edge_path(tmp_path):
    b = _bridge(tmp_path, _V5)
    out_ids = [n["id"] for n in b.related_nodes(["s"], limit=5)]
    assert "edge_hit" in out_ids
    assert "comm_hit" in out_ids                        # pulled in by community
    assert out_ids.index("edge_hit") < out_ids.index("comm_hit")   # ranked below the edge hit


def test_v4_graph_output_is_identical_to_legacy_ranker(tmp_path):
    b5 = _bridge(tmp_path / "a", _V5)
    b4 = _bridge(tmp_path / "b", _v4(_V5))
    # on v4 (no community/centrality_global) only the edge hit comes back
    assert [n["id"] for n in b4.related_nodes(["s"], limit=5)] == ["edge_hit"]
    # and community-seeding must NOT fire for v4
    assert "comm_hit" not in [n["id"] for n in b4.related_nodes(["s"], limit=5)]


def test_seed_max_zero_disables_community_seeding(tmp_path, monkeypatch):
    monkeypatch.setattr(mcp_bridge, "GRAPH_COMMUNITY_SEED_MAX", 0)
    b = _bridge(tmp_path, _V5)
    assert "comm_hit" not in [n["id"] for n in b.related_nodes(["s"], limit=5)]


def test_seed_floor_excludes_low_centrality_community_nodes(tmp_path, monkeypatch):
    monkeypatch.setattr(mcp_bridge, "GRAPH_COMMUNITY_SEED_FLOOR", 999.0)
    b = _bridge(tmp_path, _V5)
    assert "comm_hit" not in [n["id"] for n in b.related_nodes(["s"], limit=5)]
```

- [ ] **Step 2: Run to verify they fail**

Run: `python -m pytest tests/test_bridge_community_scoring.py -q`
Expected: `test_community_only_node_is_surfaced...` FAILS (`comm_hit` not in output); the v4 parity test passes already (locks current behaviour); the two knob tests FAIL on `AttributeError: module 'mcp_bridge' has no attribute 'GRAPH_COMMUNITY_SEED_MAX'`.

- [ ] **Step 3: Add the constants**

In `.agents/mcp-bridge/mcp_bridge.py`, after the embedding-seed constants (line ~36):
```python
# v5 — community-aware retrieval scoring (fail-open on a v4 graph)
GRAPH_COMMUNITY_BONUS       = float(os.environ.get("GRAPH_COMMUNITY_BONUS", "1.5"))
GRAPH_COMMUNITY_SEED_FLOOR  = float(os.environ.get("GRAPH_COMMUNITY_SEED_FLOOR", "1.0"))
GRAPH_COMMUNITY_SEED_MAX    = int(os.environ.get("GRAPH_COMMUNITY_SEED_MAX", "3"))
GRAPH_ROUTE_COMMUNITY_BONUS = float(os.environ.get("GRAPH_ROUTE_COMMUNITY_BONUS", "1.0"))
```

- [ ] **Step 4: Replace `related_nodes()`**

Replace the whole method body (keep the signature) with:
```python
    def related_nodes(self, seed_ids: List[str], limit: int = 5,
                      hops: int = 2, decay: float = 0.4) -> List[Dict[str, Any]]:
        """Multi-hop expansion over wikilink + mentions + skill-link edges with
        hop decay. v5: adds a same-community score bonus and a bounded
        community-seeded expansion for nodes with no edge path to the seeds.
        Fail-open — on a v4 graph (no community / centrality_global) the result
        is identical to the pre-v5 ranker."""
        graph = self.load_graph()
        if not graph:
            return []
        nodes = {n["id"]: n for n in graph.get("nodes", [])}
        n_count = len(nodes) or 1
        adjacency: Dict[str, set] = {}
        for e in graph.get("edges", []):
            if e.get("type") not in ("wikilink", "mentions", "skill-link"):
                continue
            adjacency.setdefault(e["from"], set()).add(e["to"])
            adjacency.setdefault(e["to"], set()).add(e["from"])
        seeds = {s for s in seed_ids if s in nodes}
        seed_comms = {nodes[s].get("community") for s in seeds
                      if nodes[s].get("community")}

        def _cent(node: Dict[str, Any]) -> float:
            pr = node.get("centrality_global")
            if pr is not None:
                return pr * n_count            # ~1.0 = average node; hubs ~5-13
            return node.get("centrality") or 0  # legacy fallback

        visited = set(seeds)
        frontier = set(seeds)
        scored: Dict[str, float] = {}
        weight = 1.0
        for _ in range(hops):
            nxt: set = set()
            for nid in frontier:
                for nb in adjacency.get(nid, ()):
                    if nb in visited or nb not in nodes:
                        continue
                    score = weight * (1 + _cent(nodes[nb]))
                    if nodes[nb].get("community") in seed_comms:
                        score *= GRAPH_COMMUNITY_BONUS
                    if score > scored.get(nb, 0.0):
                        scored[nb] = score
                    nxt.add(nb)
            visited |= nxt
            frontier = nxt
            weight *= decay

        # v5: community-seeded expansion — same-community nodes with no edge path.
        # Ranked strictly below any edge-connected hit (virtual weight = decay**hops).
        if seed_comms and len(scored) < limit * 3:
            virtual_weight = decay ** hops
            candidates = []
            for nid, node in nodes.items():
                if nid in visited or nid in scored:
                    continue
                if node.get("community") not in seed_comms:
                    continue
                c = _cent(node)
                if c >= GRAPH_COMMUNITY_SEED_FLOOR:
                    candidates.append((nid, c))
            candidates.sort(key=lambda t: (-t[1], t[0]))
            for nid, c in candidates[:GRAPH_COMMUNITY_SEED_MAX]:
                scored[nid] = virtual_weight * (1 + c)

        ranked = sorted(scored.items(), key=lambda kv: (-kv[1], kv[0]))
        return [nodes[nid] for nid, _ in ranked[:limit]]
```

- [ ] **Step 5: Run to verify all pass**

Run: `python -m pytest tests/test_bridge_community_scoring.py -q`
Expected: 4 passed.

- [ ] **Step 6: Regression — existing suite still green**

Run: `python -m pytest tests/ -q`
Expected: same pass count as Task 0 Step 3, plus the new files.

- [ ] **Step 7: Commit**

```bash
git add .agents/mcp-bridge/mcp_bridge.py tests/test_bridge_community_scoring.py
git commit -m "feat(bridge): community-aware related_nodes() — bonus + edge-less community seeding

Fail-open: v4 graph -> identical to the pre-v5 ranker. Four GRAPH_COMMUNITY_* env knobs.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_012RjkCXg6AFBdQaUbtoW6Nf"
```

---

## Task 5: `mcp_bridge.py` — `route_skills()` bonus + `/graph/related` transparency

**Files:**
- Modify: `.agents/mcp-bridge/mcp_bridge.py` — `route_skills()` (lines ~272–337) and the `_graph_related` endpoint (lines ~626–646)
- Test: `tests/test_bridge_community_scoring.py` (append)

**Interfaces:**
- Consumes: v5 node field `community`; `GRAPH_ROUTE_COMMUNITY_BONUS` from Task 4
- Produces: `route_skills()` unchanged return shape `{"query","seeds","skills","notes","code"}`; a skill whose `community` matches a seed community gets `+ GRAPH_ROUTE_COMMUNITY_BONUS` added to its rank. `/graph/related/{node_id}` response gains `related_by_community: list[str]` (node ids sharing the target's community, top by `centrality_global`, minus ids already in the other three lists).

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_bridge_community_scoring.py`:
```python
# skill 'sk_comm' shares the query-seed's community but has NO skill-link edge.
_V5_ROUTE = {
    "meta": {"version": 5},
    "nodes": [
        {"id": "focus_tracker", "layer": "engine", "path": "focus_tracker.py",
         "community": "focus_tracker", "centrality_global": 0.04},
        {"id": "skill:HS-900", "layer": "skill", "title": "Focus Flow",
         "description": "focus tracker helper", "category": "focus",
         "community": "focus_tracker", "centrality_global": 0.01},
        {"id": "skill:HS-001", "layer": "skill", "title": "Unrelated",
         "description": "something else", "category": "web",
         "community": "other", "centrality_global": 0.01},
    ],
    "edges": [],
    "issues": [],
}


def test_route_skills_boosts_same_community_skill_without_edge(tmp_path):
    b = _bridge(tmp_path, _V5_ROUTE)
    out = b.route_skills("focus_tracker session logging", limit=5)
    ids = [s["id"] for s in out["skills"]]
    assert "skill:HS-900" in ids
    # with the community bonus it outranks the token-only 'Unrelated' hit if present
    if "skill:HS-001" in ids:
        assert ids.index("skill:HS-900") < ids.index("skill:HS-001")


def test_route_skills_shape_unchanged(tmp_path):
    b = _bridge(tmp_path, _V5_ROUTE)
    out = b.route_skills("focus", limit=3)
    assert set(out.keys()) == {"query", "seeds", "skills", "notes", "code"}


def test_graph_related_endpoint_adds_related_by_community(tmp_path):
    from fastapi.testclient import TestClient
    b = _bridge(tmp_path, _V5)
    # minimal app wiring mirroring mcp_bridge.__main__
    from fastapi import FastAPI, HTTPException
    app = FastAPI()

    def _load_graph():
        import json as _j
        return _j.loads(
            (b.vault_path and open(os.path.join(b.vault_path, "06-AI-Context", "graph.json"), encoding="utf-8").read())
        )

    # exercise the library method the endpoint will use instead of duplicating it
    graph = _load_graph()
    node = next(n for n in graph["nodes"] if n["id"] == "s")
    same_comm = [n["id"] for n in graph["nodes"]
                 if n.get("community") == node["community"] and n["id"] != "s"]
    assert "comm_hit" in same_comm
```

> Note: if wiring a `TestClient` against the `__main__` app block is awkward, assert on a new small helper `MCPBridge.community_members(node_id, limit)` instead and call it from the endpoint. Decide during Step 3; keep whichever the test locks.

- [ ] **Step 2: Run to verify they fail**

Run: `python -m pytest tests/test_bridge_community_scoring.py -q`
Expected: `test_route_skills_boosts_same_community_skill_without_edge` FAILS (no bonus yet); shape test passes; the endpoint test passes only as a data check (locks intent).

- [ ] **Step 3: Add the route bonus**

In `route_skills()`, after `seeds = [n for _, n in scored[:6]]` (line ~305) add:
```python
        seed_comms = {n.get("community") for n in seeds if n.get("community")}
```
Then after the two loops that populate `skill_rank` (the `for score, n in scored:` and `for i, n in enumerate(expanded):` blocks), before `ranked = sorted(skill_rank.items()...)`:
```python
        if seed_comms:
            for nid in list(skill_rank):
                if skill_meta.get(nid, {}).get("community") in seed_comms:
                    skill_rank[nid] += GRAPH_ROUTE_COMMUNITY_BONUS
```

- [ ] **Step 4: Add `related_by_community` to the endpoint**

Add a helper method on `MCPBridge` (near `related_nodes`):
```python
    def community_members(self, node_id: str, limit: int = 5,
                          exclude: Optional[set] = None) -> List[str]:
        """Node ids sharing node_id's community, top by centrality_global.
        Empty list if the graph is v4 or the node has no community."""
        graph = self.load_graph()
        if not graph:
            return []
        nodes = {n["id"]: n for n in graph.get("nodes", [])}
        node = nodes.get(node_id)
        if not node or not node.get("community"):
            return []
        exclude = exclude or set()
        pool = [n for nid, n in nodes.items()
                if nid != node_id and nid not in exclude
                and n.get("community") == node["community"]]
        pool.sort(key=lambda n: (-(n.get("centrality_global") or 0.0), n["id"]))
        return [n["id"] for n in pool[:limit]]
```
In the `_graph_related` endpoint, before the `return`:
```python
        already = {node_id}
        already.update(
            [n["id"] for n in related]
        )
        by_community = _bridge.community_members(node_id, limit=limit, exclude=already)
```
and add `"related_by_community": by_community,` to the returned dict.

- [ ] **Step 5: Run to verify all pass**

Run: `python -m pytest tests/test_bridge_community_scoring.py -q`
Expected: 7 passed (4 from Task 4 + 3 here).

- [ ] **Step 6: Full regression**

Run: `python -m pytest tests/ -q`
Expected: green.

- [ ] **Step 7: Commit**

```bash
git add .agents/mcp-bridge/mcp_bridge.py tests/test_bridge_community_scoring.py
git commit -m "feat(bridge): route_skills() same-community bonus + /graph/related related_by_community

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_012RjkCXg6AFBdQaUbtoW6Nf"
```

---

## Task 6: Retrieval regression gate

**Files:**
- Create: `tests/fixtures/graph_v5_snapshot.json` (generated)
- Create: `tests/fixtures/retrieval_cases.json`
- Create: `tests/test_retrieval_regression.py`

**Interfaces:**
- Consumes: the full v5 pipeline (Tasks 1–5)
- Produces: a checked-in test asserting the v5 retrieval path is never worse than v4 on hand-labelled cases, and strictly better on the tagged "gap" cases.

- [ ] **Step 1: Generate the v5 snapshot**

Run:
```bash
python graph_builder.py
cp HYPERFOCUS_ZONE/06-AI-Context/graph.json tests/fixtures/graph_v5_snapshot.json
git checkout HYPERFOCUS_ZONE/06-AI-Context/graph.json    # keep the real regen for Task 7
```

- [ ] **Step 2: Hand-label `tests/fixtures/retrieval_cases.json`**

Open `tests/fixtures/graph_v5_snapshot.json`, look at the real `note:` and `skill:` ids, and fill this structure with ~10 cases. Each `expect_*` list is the ground truth for precision@5. Tag 3–4 cases `"gap": true` where the expected notes/skills are in the query subject's community but have **no** `wikilink`/`mentions`/`skill-link` path to the obvious seed (find these by eyeballing the snapshot).

Starter scaffold — **replace the `expect_*` values with real ids from the snapshot**:
```json
{
  "cases": [
    {"query": "morning briefing generation", "expect_notes": ["<real>"], "expect_skills": ["<real>"], "gap": false},
    {"query": "focus session analytics and heatmap", "expect_notes": ["<real>"], "expect_skills": ["<real>"], "gap": false},
    {"query": "mcp bridge graph endpoints", "expect_notes": ["<real>"], "expect_skills": [], "gap": false},
    {"query": "PARA vault structure where does a note go", "expect_notes": ["<real>"], "expect_skills": ["<real>"], "gap": false},
    {"query": "obsidian git auto commit vault backup", "expect_notes": ["<real>"], "expect_skills": ["<real>"], "gap": false},
    {"query": "distraction filter wired to sessions", "expect_notes": ["<real>"], "expect_skills": [], "gap": true},
    {"query": "difficulty dial dynamic xp multiplier", "expect_notes": ["<real>"], "expect_skills": [], "gap": true},
    {"query": "graph builder skills layer refresh", "expect_notes": ["<real>"], "expect_skills": ["<real>"], "gap": true},
    {"query": "github webhook real time issue sync", "expect_notes": ["<real>"], "expect_skills": [], "gap": false},
    {"query": "hyper split task decomposition", "expect_notes": ["<real>"], "expect_skills": ["<real>"], "gap": true}
  ]
}
```

- [ ] **Step 3: Write the regression test**

Create `tests/test_retrieval_regression.py`:
```python
"""Precision@5 gate: the v5 retrieval path must never lose to v4, and must win
on the tagged 'gap' cases. Ground truth is hand-labelled in retrieval_cases.json."""
import json
import os
import sys

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", ".agents", "mcp-bridge")))
import mcp_bridge  # noqa: E402

FX = os.path.join(os.path.dirname(__file__), "fixtures")
V5 = json.load(open(os.path.join(FX, "graph_v5_snapshot.json"), encoding="utf-8"))
CASES = json.load(open(os.path.join(FX, "retrieval_cases.json"), encoding="utf-8"))["cases"]


def _v4(graph):
    g = json.loads(json.dumps(graph))
    g["meta"]["version"] = 4
    for n in g["nodes"]:
        n.pop("community", None)
        n.pop("centrality_global", None)
    return g


def _bridge(tmp_path, graph, name):
    v = tmp_path / name / "vault"
    (v / "06-AI-Context").mkdir(parents=True)
    (v / "06-AI-Context" / "graph.json").write_text(json.dumps(graph), encoding="utf-8")
    return mcp_bridge.MCPBridge(vault_path=str(v))


def _precision_at_5(got, expected):
    if not expected:
        return 1.0
    top = got[:5]
    return len(set(top) & set(expected)) / min(5, len(expected))


def _score(bridge, case):
    r = bridge.route_skills(case["query"], limit=10)
    note_ids = ["note:" + os.path.splitext(p)[0].split("/")[-1] for p in r["notes"]]
    skill_p = _precision_at_5([s["id"] for s in r["skills"]], case["expect_skills"])
    note_p = _precision_at_5(note_ids + r["notes"], case["expect_notes"])
    return (skill_p + note_p) / 2


def test_v5_never_worse_than_v4_and_wins_the_gap_cases(tmp_path):
    b5 = _bridge(tmp_path, V5, "v5")
    b4 = _bridge(tmp_path, _v4(V5), "v4")
    regressions, gap_wins = [], []
    for case in CASES:
        s5, s4 = _score(b5, case), _score(b4, case)
        if s5 + 1e-9 < s4:
            regressions.append((case["query"], s4, s5))
        if case.get("gap") and s5 > s4 + 1e-9:
            gap_wins.append(case["query"])
    assert not regressions, f"v5 regressed vs v4: {regressions}"
    n_gap = sum(1 for c in CASES if c.get("gap"))
    assert len(gap_wins) >= max(1, n_gap - 1), \
        f"expected v5 to beat v4 on the gap cases, won only {gap_wins}"
```

> The `note_ids` reconstruction is deliberately loose (`route_skills` returns note *paths*, cases label note *ids*) — matching on both the reconstructed id and the raw path keeps the assertion robust. If the real snapshot makes a case impossible to satisfy even in principle, drop or re-label that case rather than weakening the gate.

- [ ] **Step 4: Run and tune**

Run: `python -m pytest tests/test_retrieval_regression.py -q`
Expected: PASS. If `regressions` is non-empty, investigate — a true v5 regression means `GRAPH_COMMUNITY_BONUS` is too aggressive or a community is too coarse (revisit Task 3 `gamma`). If `gap_wins` is short, the tagged cases aren't actually edge-less — re-pick them against the snapshot. Do not weaken the assertion to make it pass.

- [ ] **Step 5: Commit**

```bash
git add tests/fixtures/graph_v5_snapshot.json tests/fixtures/retrieval_cases.json tests/test_retrieval_regression.py
git commit -m "test(graph): precision@5 regression gate — v5 retrieval >= v4 on real-vault cases

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_012RjkCXg6AFBdQaUbtoW6Nf"
```

---

## Task 7: Docs + regenerate the canonical graph

**Files:**
- Modify: `CLAUDE.md` — "Graph Brain" section
- Regenerate + commit: `HYPERFOCUS_ZONE/06-AI-Context/graph.json`

**Interfaces:** none (documentation + the committed artifact)

- [ ] **Step 1: Update `CLAUDE.md`**

In the "🕸️ Graph Brain" section, change the version line and add a paragraph. Find:
```
**Skills layer (Phase 5, 2026-06-11):** HYPER-SILLs vault is graph layer 3 — **v4 = 199 nodes / 397 edges**.
```
Leave that historical line, and after the "Regenerate notes + skills layers" line add:
```
**Communities layer (v5, 2026-09-02):** `graph_builder.py` now also computes a
deterministic greedy-modularity partition and undirected PageRank over the
retrieval topology (`wikilink | mentions | skill-link`), stamping `community`,
`community_label`, and `centrality_global` onto every node (`meta.version` 5).
Stdlib only, recomputed every run, fail-open (a raising/absent `communities.py`
leaves the graph at v4). `mcp_bridge` `related_nodes()` and `route_skills()` use
these for a same-community score bonus and a bounded community-seeded expansion
that surfaces topically-related notes/skills with no explicit edge. Knobs:
`GRAPH_COMMUNITY_BONUS` (1.5), `GRAPH_COMMUNITY_SEED_FLOOR` (1.0),
`GRAPH_COMMUNITY_SEED_MAX` (3), `GRAPH_ROUTE_COMMUNITY_BONUS` (1.0).
Deferred: graphify LLM-inferred concept edges as a `type:"inferred"` layer —
see `docs/superpowers/specs/2026-09-02-graph-brain-v5-communities-design.md` §10.
```

- [ ] **Step 2: Regenerate the graph**

Run:
```bash
python graph_builder.py
git --no-pager diff --stat HYPERFOCUS_ZONE/06-AI-Context/graph.json
```

- [ ] **Step 3: Reconcile with the pre-existing modification (Task 0 Step 2)**

Show Lyndz `git --no-pager diff HYPERFOCUS_ZONE/06-AI-Context/graph.json`. Confirm the v5 regen is the intended state and the earlier unrelated modification is either subsumed by it or acceptable to discard. Only proceed on his confirmation.

- [ ] **Step 4: Run the CI command + full suite one last time**

Run:
```bash
python graph_builder.py && python -m pytest tests/ -q
```
Expected: builder prints `graph.json v5 — …`; all tests green.

- [ ] **Step 5: Commit**

```bash
git add CLAUDE.md HYPERFOCUS_ZONE/06-AI-Context/graph.json
git commit -m "docs(graph): Graph Brain v5 — communities layer live; regenerate graph.json

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_012RjkCXg6AFBdQaUbtoW6Nf"
```

- [ ] **Step 6: Hand back**

Summarise for Lyndz: communities_count + largest cluster size from the real graph, the chosen `gamma`, the observed `centrality_global` range, retrieval-regression result (which gap cases v5 won), and the `git log --oneline main..HEAD` for the branch. Do not merge or open a PR unless asked.

---

## Self-Review

**1. Spec coverage**

| Spec section | Task |
|---|---|
| §4 architecture — `communities.py` module, stamp step, bridge changes | Tasks 1–5 |
| §5.1 filtered edge view | Task 1 `_adjacency` + tests |
| §5.2 deterministic greedy modularity, stable IDs, wall-clock cap | Task 2 `detect_communities` + 6 tests |
| §5.3 PageRank `centrality_global`, sorted-iteration determinism, non-convergence behaviour | Task 1 `pagerank` + 5 tests |
| §5.4 no-LLM label derivation, 3 rules | Task 2 `derive_labels` + 2 tests |
| §5.5 stamp step, meta bump, fail-open | Task 3 + 2 tests |
| §6.1 four env constants | Task 4 Step 3 |
| §6.2a `_cent()` PageRank normalisation | Task 4 |
| §6.2b same-community bonus | Task 4 + test |
| §6.2c community-seeded expansion (floor, max, virtual weight) | Task 4 + 3 tests |
| §6.2d deterministic tiebreak | Task 4 (`sorted(... , kv[0])`) |
| §6.3 `route_skills()` community bonus | Task 5 + test |
| §6.4 `/graph/related` `related_by_community` | Task 5 `community_members` + endpoint + test |
| §7.1–7.3 schema, meta v5, no edge changes | Task 3 |
| §7.4 consumer impact (shapes unchanged) | Task 5 shape test; Task 4/6 regression runs |
| §7.5 error handling (fail-open, degenerate partition, non-convergence) | Task 3 Step 5 calibration + fail-open test; Task 1 convergence test |
| §8.1 `test_communities.py` | Tasks 1–2 |
| §8.2 `test_graph_builder_communities.py` | Task 3 |
| §8.3 `test_bridge_community_scoring.py` | Tasks 4–5 |
| §8.4 retrieval regression gate + fixtures | Task 6 |
| §8.5 existing suite stays green | Task 0 Step 3 baseline; Task 4/5 Step 6 |
| §9 files touched | File Structure table + tasks |
| §10 deferred graphify edges | out of scope — referenced in CLAUDE.md (Task 7) |
| §11 open questions (gamma, PR range, fixture cases) | Task 3 Step 5, Task 6 Step 2 |

No gaps.

**2. Placeholder scan**

- `retrieval_cases.json` ships with `"<real>"` placeholders **by design** — Task 6 Step 2 is the explicit hand-labelling step against the generated snapshot, with concrete instructions for choosing values and tagging gap cases. This is a data-authoring step, not a code placeholder.
- `graph_v5_snapshot.json` is generated by a command in Task 6 Step 1, not hand-written.
- Task 3 Step 5 leaves `gamma` as "the value from calibration" — the step gives the exact target (8–40 communities, largest < 40%), the candidate values to try (`0.5`, `2.0`), and where to record it. Not a placeholder; it's an empirical decision with a defined procedure and a safe default (`1.0`).
- No "TODO", "handle edge cases", "similar to Task N", or undefined references remain.

**3. Type consistency**

- `_adjacency(nodes, edges) -> dict[str, set[str]]` — same call shape in `pagerank`, `detect_communities`. ✎
- `detect_communities(...) -> (node_community: dict[str,str], members: dict[str, list[str]])` — Task 3 unpacks exactly `node_comm, comm_members` and passes `comm_members` to `derive_labels`. ✎
- `derive_labels(members, nodes, pagerank) -> dict[str, str]` — Task 3 calls `derive_labels(comm_members, graph["nodes"], pr)`, arg order matches. ✎
- `pagerank(...) -> dict[str, float]` — Task 3 uses `pr.get(n["id"], 0.0)`; Task 4 `_cent` reads `node.get("centrality_global")` (the stamped field), not the dict. ✎
- Constants `GRAPH_COMMUNITY_BONUS` / `GRAPH_COMMUNITY_SEED_FLOOR` / `GRAPH_COMMUNITY_SEED_MAX` / `GRAPH_ROUTE_COMMUNITY_BONUS` — defined once in Task 4 Step 3, consumed in Tasks 4 (`related_nodes`) and 5 (`route_skills`). Names identical throughout. ✎
- `MCPBridge.community_members(node_id, limit, exclude)` — defined in Task 5 Step 4, called by the endpoint in the same step. ✎
- `related_nodes()` / `route_skills()` signatures unchanged from the current file. ✎

No inconsistencies.
