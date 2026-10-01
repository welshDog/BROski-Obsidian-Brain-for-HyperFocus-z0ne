# Graph Brain §10 — Inferred Concept Edges Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the deferred §10 increment of the Graph Brain v5 spec — a scoped, host/CI-only `graphify` pass that extracts only high-confidence `INFERRED` concept edges and feeds them into the canonical `graph.json` as an optional, fail-open `inferred` edge layer that `mcp_bridge.py` can traverse at reduced weight.

**Architecture:** `scripts/graph_enrich.py` is a new, standalone, non-stdlib script that shells out to the headless `graphify extract` CLI (scoped with `--exclude` to skip `.obsidian/`, `node_modules/`, `brain-bundle*`, `openhuman-build/`, minified JS), filters its raw extraction down to `INFERRED` edges with `confidence_score >= 0.7`, remaps both endpoints to canonical graph IDs by source file, drops anything that duplicates an existing `wikilink`/`mentions`/`skill-link` edge or that fails to map, and atomically writes the survivors to `HYPERFOCUS_ZONE/06-AI-Context/graph_inferred_edges.json`. `graph_builder.py` gains an optional merge step that loads that sidecar file (file absent = no-op) and appends its edges as `{"type": "inferred"}`, validating both endpoints still exist in the current graph. `mcp_bridge.py`'s `related_nodes()` adds `"inferred"` to its traversal allow-list at a lower per-edge weight than the three existing types. `communities.py` (native community/PageRank detection) is untouched — it keeps its own `FILTERED_EDGE_TYPES` and never sees `inferred` edges, preserving the spec's "no dependency from C on this increment" rule.

**Tech Stack:** Python 3 stdlib for `graph_builder.py`/`mcp_bridge.py`/tests (existing convention); `graphifyy` PyPI package (via its `graphify` CLI, invoked through `subprocess`) is the one permitted non-stdlib dependency, confined entirely to `scripts/graph_enrich.py`. Test runner: `pytest`, matching the existing `tests/` suite.

**Spec:** `docs/superpowers/specs/2026-09-02-graph-brain-v5-communities-design.md`, §10 ("Deferred increment — graphify LLM-inferred concept edges"). Sections 1–9 of that spec (native communities + PageRank) are already shipped and live in `graph_builder.py` / `communities.py` / `mcp_bridge.py` — this plan touches none of that machinery except to add the one optional merge point §10 describes.

## Global Constraints

- `graph_builder.py`, `communities.py`, and `mcp_bridge.py` stay stdlib-only / zero new dependencies (spec §1, §5). `scripts/graph_enrich.py` is the single, deliberate exception — it is host/CI-only and may depend on the `graphifyy` package.
- Communities + centrality stay native to `communities.py`: its `FILTERED_EDGE_TYPES = ("wikilink", "mentions", "skill-link")` is **not** touched, and `"inferred"` is never added to it (spec §10: "no dependency from C on this increment").
- An inferred edge qualifies only if `confidence == "INFERRED"` **and** `confidence_score >= 0.7` (spec §10, open question defaults settled here since §10 states the threshold explicitly). `EXTRACTED` and `AMBIGUOUS` edges are never considered.
- Dedup rule: an inferred edge whose unordered `(from, to)` pair already exists as a `wikilink`, `mentions`, or `skill-link` edge in the canonical graph is dropped (spec §10).
- Missing `graph_inferred_edges.json` = no-op everywhere — same fail-open convention as the skills-repo-unreachable preserve-mode already in `graph_builder.py`'s `scan_skills()`.
- Canonical ID formats (must match `graph_builder.py` exactly, **not** graphify's own `{parent_dir}_{stem}_{entity}` convention): vault notes → `note:<basename-without-.md>`; skills → `skill:HS-###`; every other layer (`monolith`/`engine`/`agent`/`root`/`dead`/`aifs`) → the bare module filename stem with no path prefix (e.g. `hyper_brain_core`).
- `mcp_bridge.py`: `"inferred"` edges are weighted strictly below `wikilink`/`mentions`/`skill-link` (default `0.5`, overridable via `GRAPH_INFERRED_EDGE_WEIGHT`). `related_nodes()`'s existing behavior on a graph with **no** inferred edges must be provably unchanged.
- `graph_inferred_edges.json` is written atomically (`tempfile.mkstemp` + `os.replace`), matching `graph_builder.py`'s existing write pattern for `graph.json` — never a half-written file read by a concurrent process.
- `scripts/graph_enrich.py` must **never** fail destructively: if `graphify` isn't installed, no API key is set, or the extraction errors, it leaves any existing `graph_inferred_edges.json` untouched and exits 0.

## Review Focus

- A `graph_inferred_edges.json` edge references a node that existed when `graph_enrich.py` ran but was deleted/renamed by the next `graph_builder.py` run (vault note removed, module deleted) — must be silently dropped, never crash the build. → Task 1.
- `graph_enrich.py` runs on a fresh host with no `GEMINI_API_KEY` or without `graphify` on `PATH` — must exit cleanly, touch nothing, and never fail `graph_builder.py`'s next run. → Task 2.
- A graphify-extracted concept edge whose two endpoints both collapse to the *same* canonical id (e.g. two functions inside one tracked module) must not produce a self-loop edge. → Task 2.
- `communities.py`/PageRank output must be byte-identical whether or not an inferred layer is present — a careless change that added `"inferred"` to `FILTERED_EDGE_TYPES` would silently shift every community/centrality number in production. → Task 1 (no touch) + Task 3 (regression re-run).
- Every Brain deployment that has never run `graph_enrich.py` (i.e. no `inferred` edges exist in `graph.json` at all) must see `mcp_bridge.py` behave exactly as before this change — a bug in the new weighted-adjacency code could silently alter `wikilink`/`mentions`/`skill-link` scoring even at weight `1.0`. → Task 3.

---

### Task 1: `graph_builder.py` — optional inferred-edges merge

**Files:**
- Modify: `graph_builder.py:276-336` (`merge()`), `graph_builder.py:339-392` (`main()`)
- Test: `tests/test_inferred_edges_merge.py` (new)

**Interfaces:**
- Produces: `graph_builder.load_inferred_edges(node_ids: set[str], inferred_path: str | None) -> list[dict]` — each dict is `{"from": str, "to": str, "type": "inferred", "relation": str | None, "confidence_score": float | None}`.
- Modifies: `graph_builder.merge(graph, note_nodes, note_edges, mention_edges, notes_scanned, skill_nodes=None, skill_edges=None, inferred_path=None) -> dict` — new optional trailing kwarg, fully backward compatible (all existing call sites omit it and get the old no-inferred-layer behavior).
- Consumes (Task 2's output contract): `graph_inferred_edges.json` shaped `{"generated": str, "source": str, "min_confidence": float, "edges": [{"from": str, "to": str, "relation": str, "confidence_score": float}, ...]}`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_inferred_edges_merge.py
"""merge() optional inferred-edges layer (spec §10) -- file absent = no-op,
stale/unmappable endpoints dropped, survives communities fail-open, never
accumulates across runs."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import graph_builder  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MINI = os.path.join(os.path.dirname(__file__), "fixtures", "mini_vault")


def _base_graph():
    return {
        "meta": {},
        "nodes": [
            {"id": "x", "layer": "code", "path": "x.py", "centrality": 0, "status": "live"},
            {"id": "y", "layer": "code", "path": "y.py", "centrality": 0, "status": "live"},
        ],
        "edges": [],
        "issues": [],
    }


def test_missing_inferred_file_is_a_noop(tmp_path):
    out = graph_builder.merge(_base_graph(), [], [], [], 0,
                               skill_nodes=[], skill_edges=[],
                               inferred_path=str(tmp_path / "does-not-exist.json"))
    assert out["meta"].get("inferred_edges_count", 0) == 0
    assert "inferred" not in out["meta"]["layers"]
    assert all(e.get("type") != "inferred" for e in out["edges"])


def test_inferred_edges_merged_when_both_endpoints_exist(tmp_path):
    inferred_path = tmp_path / "graph_inferred_edges.json"
    inferred_path.write_text(json.dumps({"edges": [
        {"from": "x", "to": "y", "relation": "conceptually_related_to", "confidence_score": 0.85},
    ]}), encoding="utf-8")
    out = graph_builder.merge(_base_graph(), [], [], [], 0,
                               skill_nodes=[], skill_edges=[],
                               inferred_path=str(inferred_path))
    inferred = [e for e in out["edges"] if e.get("type") == "inferred"]
    assert len(inferred) == 1
    assert inferred[0]["from"] == "x" and inferred[0]["to"] == "y"
    assert inferred[0]["confidence_score"] == 0.85
    assert out["meta"]["inferred_edges_count"] == 1
    assert "inferred" in out["meta"]["layers"]


def test_inferred_edge_with_stale_endpoint_is_dropped(tmp_path):
    inferred_path = tmp_path / "graph_inferred_edges.json"
    inferred_path.write_text(json.dumps({"edges": [
        {"from": "x", "to": "deleted_module", "relation": "shares_data_with", "confidence_score": 0.9},
    ]}), encoding="utf-8")
    out = graph_builder.merge(_base_graph(), [], [], [], 0,
                               skill_nodes=[], skill_edges=[],
                               inferred_path=str(inferred_path))
    assert out["meta"].get("inferred_edges_count", 0) == 0
    assert all(e.get("type") != "inferred" for e in out["edges"])


def test_inferred_edge_self_loop_is_dropped(tmp_path):
    inferred_path = tmp_path / "graph_inferred_edges.json"
    inferred_path.write_text(json.dumps({"edges": [
        {"from": "x", "to": "x", "relation": "self", "confidence_score": 0.9},
    ]}), encoding="utf-8")
    out = graph_builder.merge(_base_graph(), [], [], [], 0,
                               skill_nodes=[], skill_edges=[],
                               inferred_path=str(inferred_path))
    assert out["meta"].get("inferred_edges_count", 0) == 0


def test_inferred_layer_survives_communities_fail_open(monkeypatch, tmp_path):
    def _boom(*a, **k):
        raise RuntimeError("boom")
    monkeypatch.setattr("communities.pagerank", _boom)
    inferred_path = tmp_path / "graph_inferred_edges.json"
    inferred_path.write_text(json.dumps({"edges": [
        {"from": "x", "to": "y", "relation": "r", "confidence_score": 0.8},
    ]}), encoding="utf-8")
    out = graph_builder.merge(_base_graph(), [], [], [], 0,
                               skill_nodes=[], skill_edges=[],
                               inferred_path=str(inferred_path))
    assert out["meta"]["version"] == 4
    assert "inferred" in out["meta"]["layers"]
    assert out["meta"]["inferred_edges_count"] == 1


def test_rebuild_drops_previously_merged_inferred_edges_not_in_sidecar_anymore(tmp_path):
    """Inferred edges are not accumulated -- each run reflects only the
    current sidecar file, same convention as the notes/skills layers."""
    graph = _base_graph()
    graph["edges"] = [{"from": "x", "to": "y", "type": "inferred",
                        "relation": "stale", "confidence_score": 0.7}]
    out = graph_builder.merge(graph, [], [], [], 0,
                               skill_nodes=[], skill_edges=[],
                               inferred_path=str(tmp_path / "does-not-exist.json"))
    assert all(e.get("type") != "inferred" for e in out["edges"])


def _run_builder(vault, extra_env=None):
    env = dict(os.environ)
    env["BRAIN_SKILLS_PATH"] = os.path.join(vault, "_no_skills_here")
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [sys.executable, "graph_builder.py", "--vault", vault],
        cwd=REPO, env=env, capture_output=True, text=True,
    )


def test_integration_cli_merges_inferred_sidecar_next_to_graph_json():
    with tempfile.TemporaryDirectory() as tmp:
        vault = os.path.join(tmp, "HYPERFOCUS_ZONE")
        shutil.copytree(MINI, vault)
        inferred_path = os.path.join(vault, "06-AI-Context", "graph_inferred_edges.json")
        with open(inferred_path, "w", encoding="utf-8") as f:
            json.dump({"edges": [
                {"from": "note:Delta", "to": "hyper_brain_core",
                 "relation": "conceptually_related_to", "confidence_score": 0.8},
            ]}, f)
        proc = _run_builder(vault)
        assert proc.returncode == 0, proc.stderr
        graph = json.load(open(os.path.join(vault, "06-AI-Context", "graph.json"), encoding="utf-8"))
        inferred = [e for e in graph["edges"] if e.get("type") == "inferred"]
        assert len(inferred) == 1
        assert "inferred" in graph["meta"]["layers"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_inferred_edges_merge.py -v`
Expected: FAIL — `merge()` has no `inferred_path` parameter yet (`TypeError: merge() got an unexpected keyword argument 'inferred_path'`).

- [ ] **Step 3: Implement `load_inferred_edges()` and wire it into `merge()`**

Add this new function just above `merge()` in `graph_builder.py` (after `_touches_skill`, before `def merge(...)`):

```python
def load_inferred_edges(node_ids, inferred_path):
    """Load scripts/graph_enrich.py's sidecar file (spec §10), dropping edges
    whose endpoints no longer exist in the current graph or that are
    self-loops after mapping. Missing/unreadable file = no-op (preserve
    contract -- this enrichment layer is entirely optional)."""
    if not inferred_path or not os.path.isfile(inferred_path):
        return []
    try:
        with open(inferred_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"inferred edges: skipped ({exc})")
        return []
    edges = []
    for e in data.get("edges", []):
        src, dst = e.get("from"), e.get("to")
        if src in node_ids and dst in node_ids and src != dst:
            edges.append({
                "from": src, "to": dst, "type": "inferred",
                "relation": e.get("relation"),
                "confidence_score": e.get("confidence_score"),
            })
    return edges
```

Replace the `merge()` signature and the `kept_edges` line:

```python
def merge(graph, note_nodes, note_edges, mention_edges, notes_scanned,
          skill_nodes=None, skill_edges=None, inferred_path=None):
    """Replace the generated layers inside the existing graph, preserve the rest.
    skill_nodes/skill_edges None = skills repo unreachable this run -- the
    previous skill layer is carried over untouched instead of being wiped.
    inferred_path (spec §10, optional) = sidecar file from
    scripts/graph_enrich.py; missing file = no inferred layer this run."""
    kept_nodes = [n for n in graph.get("nodes", [])
                  if n.get("layer") not in ("note", "skill")]
    kept_edges = [e for e in graph.get("edges", [])
                  if e.get("type") not in ("wikilink", "mentions", "skill-link", "inferred")]
```

Replace the node/edge assembly and meta-stamping block (everything from `if skill_nodes is None:` through the `meta["total_edges"] = ...` line) with:

```python
    if skill_nodes is None:
        skill_nodes = [n for n in graph.get("nodes", []) if n.get("layer") == "skill"]
        skill_edges = [e for e in graph.get("edges", [])
                       if e.get("type") in ("mentions", "skill-link") and _touches_skill(e)]
        # carried-over note→skill mentions may point at notes that no longer exist
        note_ids = {n["id"] for n in note_nodes}
        skill_edges = [e for e in skill_edges
                       if not str(e["from"]).startswith("note:") or e["from"] in note_ids]

    graph["nodes"] = kept_nodes + note_nodes + skill_nodes

    node_ids = {n["id"] for n in graph["nodes"]}
    inferred_edges = load_inferred_edges(node_ids, inferred_path)

    graph["edges"] = kept_edges + note_edges + mention_edges + skill_edges + inferred_edges

    meta = graph.setdefault("meta", {})
    meta["version"] = 4
    meta["layers"] = ["code", "notes", "mentions", "skills"]
    if inferred_edges:
        meta["layers"] = meta["layers"] + ["inferred"]
        meta["inferred_edges_count"] = len(inferred_edges)
    else:
        meta.pop("inferred_edges_count", None)
    meta["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    meta["notes_scanned"] = notes_scanned
    meta["skills_indexed"] = sum(1 for n in skill_nodes if n.get("status") != "phantom")
    meta["total_nodes"] = len(graph["nodes"])
    meta["total_edges"] = len(graph["edges"])
```

Replace the two hardcoded `meta["layers"] = [...]` lines inside the `try`/`except` communities block so they build on the (possibly inferred-including) base list instead of a fresh literal:

```python
        meta["version"] = 5
        meta["layers"] = meta["layers"] + ["communities"]
        meta["communities_count"] = len(set(node_comm.values()))
        meta["community_algo"] = "greedy-modularity"
    except Exception as exc:  # fail-open -- enrichment is non-critical; a missing or broken communities.py leaves the graph at v4
        print(f"communities: skipped ({exc})")
        for _n in graph["nodes"]:
            _n.pop("community", None)
            _n.pop("community_label", None)
            _n.pop("centrality_global", None)
        meta["layers"] = ["code", "notes", "mentions", "skills"]
        if inferred_edges:
            meta["layers"] = meta["layers"] + ["inferred"]
        meta.pop("communities_count", None)
        meta.pop("community_algo", None)
```

In `main()`, add the CLI flag and thread it through:

```python
    parser.add_argument("--inferred", default=None,
                        help="graph_inferred_edges.json path (default: "
                             "<vault>/06-AI-Context/graph_inferred_edges.json; "
                             "missing file = no inferred layer, spec §10)")
```

(add this line next to the existing `--skills` argument), and change the `merge()` call:

```python
    inferred_path = args.inferred or os.path.join(args.vault, "06-AI-Context", "graph_inferred_edges.json")
    graph = merge(graph, note_nodes, note_edges, mention_edges, len(notes),
                  skill_nodes, skill_edges, inferred_path=inferred_path)
```

and the final summary print:

```python
    inferred_count = graph["meta"].get("inferred_edges_count", 0)
    skill_count = len([n for n in graph["nodes"] if n.get("layer") == "skill"])
    print(f"graph.json v{graph['meta']['version']} — "
          f"{graph['meta']['total_nodes']} nodes / {graph['meta']['total_edges']} edges "
          f"({len(note_nodes)} note nodes, {len(note_edges)} wikilink edges, "
          f"{len(mention_edges)} mentions edges, {skill_count} skill nodes, "
          f"{inferred_count} inferred edges, {len(notes)} notes scanned)")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_inferred_edges_merge.py tests/test_graph_builder_communities.py tests/test_communities.py -v`
Expected: PASS — the new file passes, and the two pre-existing files are unaffected (they never pass `inferred_path`, so `load_inferred_edges()` short-circuits to `[]`).

- [ ] **Step 5: Commit**

```bash
git add graph_builder.py tests/test_inferred_edges_merge.py
git commit -m "feat(graph-brain): optional inferred-edges merge in graph_builder.py (spec §10)"
```

---

### Task 2: `scripts/graph_enrich.py` — scoped graphify pass, ID mapping, confidence filter

**Files:**
- Create: `scripts/graph_enrich.py`
- Test: `tests/test_graph_enrich.py` (new)

**Interfaces:**
- Consumes: nothing from Task 1 except the sidecar JSON *shape* it must produce (see Task 1's Interfaces block).
- Produces: `graph_enrich.vault_relative_md_id(source_file: str, vault_root: str) -> str | None`, `graph_enrich.code_module_id(source_file: str, code_ids: set[str]) -> str | None`, `graph_enrich.skill_id_for_file(source_file: str, skills_file_map: dict[str, str] | None) -> str | None`, `graph_enrich.map_to_canonical_id(source_file, vault_root, code_ids, skills_file_map) -> str | None`, `graph_enrich.load_skills_file_map(skills_root: str) -> dict[str, str] | None`, `graph_enrich.extract_inferred_edges(raw_extraction: dict, canonical_graph: dict, vault_root: str, skills_file_map: dict | None, min_confidence: float) -> list[dict]`, `graph_enrich.run_graphify_extract(target: str, out_dir: str, backend: str = "gemini", excludes: list[str] | None = None) -> pathlib.Path | None`, `graph_enrich.write_inferred_edges(edges: list[dict], out_path, min_confidence: float) -> None`, `graph_enrich.GRAPHIFY_EXCLUDES: list[str]`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_graph_enrich.py
"""scripts/graph_enrich.py -- ID mapping, confidence filter, dedup (spec §10).
No network/API calls: run_graphify_extract() is exercised only through a
subprocess.run / shutil.which stub that checks the CLI invocation shape."""
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))

import graph_enrich  # noqa: E402

VAULT = "/vault"

CANONICAL = {
    "nodes": [
        {"id": "hyper_brain_core", "layer": "monolith"},
        {"id": "note:Alpha", "layer": "note", "path": "01-Projects/Alpha.md"},
        {"id": "note:Beta", "layer": "note", "path": "01-Projects/Beta.md"},
        {"id": "skill:HS-900", "layer": "skill"},
    ],
    "edges": [
        {"from": "note:Alpha", "to": "note:Beta", "type": "wikilink"},
    ],
}

SKILLS_MAP = {"skills/deep-work/SKILL.md": "HS-900"}


def _raw_edge(source_id, target_id, score=0.85, relation="conceptually_related_to"):
    return {"source": source_id, "target": target_id, "relation": relation,
            "confidence": "INFERRED", "confidence_score": score}


def test_maps_vault_md_to_note_id():
    assert graph_enrich.vault_relative_md_id(
        "/vault/01-Projects/Alpha.md", VAULT) == "note:Alpha"


def test_md_outside_vault_is_unmapped():
    assert graph_enrich.vault_relative_md_id("/elsewhere/Alpha.md", VAULT) is None


def test_non_md_is_unmapped_by_note_mapper():
    assert graph_enrich.vault_relative_md_id("/vault/foo.py", VAULT) is None


def test_maps_tracked_python_module_to_its_stem():
    code_ids = {"hyper_brain_core"}
    assert graph_enrich.code_module_id(
        "/repo/scripts/hyper_brain_core.py", code_ids) == "hyper_brain_core"


def test_untracked_python_file_is_unmapped():
    code_ids = {"hyper_brain_core"}
    assert graph_enrich.code_module_id("/repo/tests/test_foo.py", code_ids) is None


def test_maps_skill_file_to_hs_id():
    assert graph_enrich.skill_id_for_file(
        "/skills-repo/skills/deep-work/SKILL.md", SKILLS_MAP) == "skill:HS-900"


def test_skill_mapping_skipped_when_registry_unreachable():
    assert graph_enrich.skill_id_for_file(
        "/skills-repo/skills/deep-work/SKILL.md", None) is None


def test_extract_inferred_edges_keeps_high_confidence_cross_layer_edge():
    raw = {
        "nodes": [
            {"id": "a", "source_file": "/vault/02-Areas/Gamma.md"},
            {"id": "b", "source_file": "/repo/hyper_brain_core.py"},
        ],
        "edges": [_raw_edge("a", "b", score=0.85)],
    }
    out = graph_enrich.extract_inferred_edges(raw, CANONICAL, VAULT, None, 0.7)
    assert out == [{"from": "note:Gamma", "to": "hyper_brain_core",
                     "relation": "conceptually_related_to", "confidence_score": 0.85}]


def test_extract_inferred_edges_drops_low_confidence():
    raw = {
        "nodes": [
            {"id": "a", "source_file": "/vault/02-Areas/Gamma.md"},
            {"id": "b", "source_file": "/repo/hyper_brain_core.py"},
        ],
        "edges": [_raw_edge("a", "b", score=0.65)],
    }
    assert graph_enrich.extract_inferred_edges(raw, CANONICAL, VAULT, None, 0.7) == []


def test_extract_inferred_edges_drops_extracted_and_ambiguous_confidence_classes():
    raw = {
        "nodes": [
            {"id": "a", "source_file": "/vault/02-Areas/Gamma.md"},
            {"id": "b", "source_file": "/repo/hyper_brain_core.py"},
        ],
        "edges": [
            {"source": "a", "target": "b", "relation": "r",
             "confidence": "EXTRACTED", "confidence_score": 1.0},
            {"source": "a", "target": "b", "relation": "r",
             "confidence": "AMBIGUOUS", "confidence_score": 0.2},
        ],
    }
    assert graph_enrich.extract_inferred_edges(raw, CANONICAL, VAULT, None, 0.7) == []


def test_extract_inferred_edges_drops_unmappable_endpoint():
    raw = {
        "nodes": [
            {"id": "a", "source_file": "/vault/02-Areas/Gamma.md"},
            {"id": "b", "source_file": "/repo/scripts/stale_mirror_script.py"},
        ],
        "edges": [_raw_edge("a", "b")],
    }
    assert graph_enrich.extract_inferred_edges(raw, CANONICAL, VAULT, None, 0.7) == []


def test_extract_inferred_edges_drops_self_loop_after_mapping():
    """Two different graphify nodes that both live in the SAME canonical file
    (e.g. two symbols in hyper_brain_core.py) must not produce a self-edge
    once mapped down to the module-level id."""
    raw = {
        "nodes": [
            {"id": "a", "source_file": "/repo/hyper_brain_core.py"},
            {"id": "b", "source_file": "/repo/hyper_brain_core.py"},
        ],
        "edges": [_raw_edge("a", "b")],
    }
    assert graph_enrich.extract_inferred_edges(raw, CANONICAL, VAULT, None, 0.7) == []


def test_extract_inferred_edges_dedupes_against_existing_wikilink():
    raw = {
        "nodes": [
            {"id": "a", "source_file": "/vault/01-Projects/Alpha.md"},
            {"id": "b", "source_file": "/vault/01-Projects/Beta.md"},
        ],
        "edges": [_raw_edge("a", "b")],
    }
    assert graph_enrich.extract_inferred_edges(raw, CANONICAL, VAULT, None, 0.7) == []


def test_extract_inferred_edges_keeps_highest_confidence_on_duplicate_pair():
    raw = {
        "nodes": [
            {"id": "a", "source_file": "/vault/02-Areas/Gamma.md"},
            {"id": "b", "source_file": "/repo/hyper_brain_core.py"},
        ],
        "edges": [
            _raw_edge("a", "b", score=0.75, relation="weak_link"),
            _raw_edge("b", "a", score=0.9, relation="strong_link"),
        ],
    }
    out = graph_enrich.extract_inferred_edges(raw, CANONICAL, VAULT, None, 0.7)
    assert len(out) == 1
    assert out[0]["confidence_score"] == 0.9
    assert out[0]["relation"] == "strong_link"


def test_run_graphify_extract_invokes_expected_cli_shape(monkeypatch, tmp_path):
    calls = {}

    def _fake_which(name):
        return "/usr/bin/graphify" if name == "graphify" else None

    def _fake_run(cmd, **kwargs):
        calls["cmd"] = cmd
        out_graphify = tmp_path / "graphify-out"
        out_graphify.mkdir(parents=True, exist_ok=True)
        (out_graphify / "graph.json").write_text("{}", encoding="utf-8")
        class _Result:
            returncode = 0
            stderr = ""
        return _Result()

    monkeypatch.setattr(graph_enrich.shutil, "which", _fake_which)
    monkeypatch.setattr(graph_enrich.subprocess, "run", _fake_run)

    result = graph_enrich.run_graphify_extract("/repo", str(tmp_path), backend="gemini")
    assert result == tmp_path / "graphify-out" / "graph.json"
    cmd = calls["cmd"]
    assert cmd[:2] == ["/usr/bin/graphify", "extract"]
    assert "--backend" in cmd and "gemini" in cmd
    assert "--no-cluster" in cmd
    assert cmd.count("--exclude") == len(graph_enrich.GRAPHIFY_EXCLUDES)


def test_run_graphify_extract_returns_none_when_graphify_not_installed(monkeypatch, tmp_path):
    monkeypatch.setattr(graph_enrich.shutil, "which", lambda name: None)
    assert graph_enrich.run_graphify_extract("/repo", str(tmp_path)) is None


def test_write_inferred_edges_is_atomic_and_round_trips(tmp_path):
    out_path = tmp_path / "06-AI-Context" / "graph_inferred_edges.json"
    edges = [{"from": "a", "to": "b", "relation": "r", "confidence_score": 0.8}]
    graph_enrich.write_inferred_edges(edges, out_path, 0.7)
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["edges"] == edges
    assert data["min_confidence"] == 0.7
    assert "generated" in data
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_graph_enrich.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'graph_enrich'` (file doesn't exist yet).

- [ ] **Step 3: Implement `scripts/graph_enrich.py`**

```python
#!/usr/bin/env python3
"""
scripts/graph_enrich.py
Graph Brain v5 §10 -- deferred increment.

Runs a SCOPED graphify pass over the vault (*.md), the Brain's own tracked
Python modules, and the HYPER-SILLs skills registry, excluding Obsidian
plugin bundles, node_modules, brain-bundle mirrors, openhuman-build, and
minified JS. Extracts only high-confidence INFERRED concept edges, remaps
both endpoints to canonical graph.json node ids, drops anything that
duplicates an existing wikilink/mentions/skill-link edge or fails to map,
and atomically writes the survivors to graph_inferred_edges.json.

graph_builder.py optionally merges that file in as an {"type": "inferred"}
edge layer (file absent = no-op). Communities/PageRank (communities.py)
never see this layer -- it stays native, per spec §10.

Host/CI only. This is the one script in the repo allowed to depend on a
non-stdlib package (the `graphifyy` PyPI package, via its `graphify` CLI).
Requires `graphify` on PATH (`pip install graphifyy` or
`uv tool install graphifyy`) and a backend API key (GEMINI_API_KEY by
default) -- missing either is a clean no-op, not a failure.

Usage:
    python scripts/graph_enrich.py
    python scripts/graph_enrich.py --backend gemini --min-confidence 0.7

BROski♾️
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_VAULT = REPO_ROOT / "HYPERFOCUS_ZONE"
DEFAULT_GRAPH = DEFAULT_VAULT / "06-AI-Context" / "graph.json"
DEFAULT_OUT = DEFAULT_VAULT / "06-AI-Context" / "graph_inferred_edges.json"
DEFAULT_SKILLS = Path(os.environ.get(
    "BRAIN_SKILLS_PATH", str(REPO_ROOT.parent / "HYPER-SILLs-By-WelshDog")))
MIN_CONFIDENCE = 0.7

GRAPHIFY_EXCLUDES = [
    ".obsidian/", "node_modules/", "brain-bundle*/", "openhuman-build/",
    "*.min.js",
]


def vault_relative_md_id(source_file, vault_root):
    """HYPERFOCUS_ZONE/**/Foo.md -> 'note:Foo'. None if not a .md file or
    outside the vault."""
    p = Path(source_file)
    if p.suffix.lower() != ".md":
        return None
    try:
        p.resolve().relative_to(Path(vault_root).resolve())
    except ValueError:
        return None
    return f"note:{p.stem}"


def code_module_id(source_file, code_ids):
    """repo/anything/hyper_brain_core.py -> 'hyper_brain_core' IFF that stem
    is already a canonical code-layer node id; else None (not a tracked
    module -- e.g. a stale scripts/ mirror or a test file)."""
    p = Path(source_file)
    if p.suffix.lower() != ".py":
        return None
    return p.stem if p.stem in code_ids else None


def skill_id_for_file(source_file, skills_file_map):
    """skills_file_map: {registry 'file' path -> HS-id}, or None when the
    skills repo was unreachable this run (preserve-mode, same convention as
    graph_builder.scan_skills)."""
    if not skills_file_map:
        return None
    norm = str(Path(source_file)).replace(os.sep, "/")
    for reg_file, sid in skills_file_map.items():
        if norm.endswith(reg_file):
            return f"skill:{sid}"
    return None


def map_to_canonical_id(source_file, vault_root, code_ids, skills_file_map):
    if not source_file:
        return None
    return (vault_relative_md_id(source_file, vault_root)
            or code_module_id(source_file, code_ids)
            or skill_id_for_file(source_file, skills_file_map))


def load_skills_file_map(skills_root):
    """Mirror graph_builder.scan_skills()'s reachability contract: None means
    the skills repo isn't checked out on this host. Callers must then skip
    skill-id mapping entirely -- never fabricate an empty-but-present map,
    which would read as 'registry has zero skills' instead of 'unreachable'."""
    registry_path = os.path.join(skills_root, "skills-registry.json")
    if not os.path.isfile(registry_path):
        return None
    with open(registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)
    file_map = {}
    for entry in registry.get("skills", []):
        sid = entry.get("id")
        file_ = entry.get("file")
        if sid and file_:
            file_map[file_.replace("\\", "/")] = sid
    return file_map


def extract_inferred_edges(raw_extraction, canonical_graph, vault_root,
                            skills_file_map, min_confidence=MIN_CONFIDENCE):
    nodes_by_id = {n["id"]: n for n in raw_extraction.get("nodes", [])}
    code_ids = {n["id"] for n in canonical_graph.get("nodes", [])
                if n.get("layer") not in ("note", "skill")}
    existing_pairs = {
        frozenset((e["from"], e["to"]))
        for e in canonical_graph.get("edges", [])
        if e.get("type") in ("wikilink", "mentions", "skill-link")
    }

    best_by_pair = {}
    for e in raw_extraction.get("edges", []):
        if e.get("confidence") != "INFERRED":
            continue
        score = e.get("confidence_score") or 0.0
        if score < min_confidence:
            continue
        src_node = nodes_by_id.get(e.get("source")) or {}
        tgt_node = nodes_by_id.get(e.get("target")) or {}
        src_file = src_node.get("source_file") or e.get("source_file")
        tgt_file = tgt_node.get("source_file") or e.get("source_file")
        from_id = map_to_canonical_id(src_file, vault_root, code_ids, skills_file_map)
        to_id = map_to_canonical_id(tgt_file, vault_root, code_ids, skills_file_map)
        if not from_id or not to_id or from_id == to_id:
            continue
        pair = frozenset((from_id, to_id))
        if pair in existing_pairs:
            continue
        current = best_by_pair.get(pair)
        if current is None or score > current["confidence_score"]:
            best_by_pair[pair] = {
                "from": from_id, "to": to_id,
                "relation": e.get("relation"),
                "confidence_score": score,
            }
    return list(best_by_pair.values())


def run_graphify_extract(target, out_dir, backend="gemini", excludes=None):
    """Shell out to the headless `graphify extract` CLI. Returns the path to
    the raw extraction graph.json, or None if graphify isn't installed or
    the run failed (fail-open -- enrichment is optional, never blocks
    graph_builder.py)."""
    graphify_bin = shutil.which("graphify")
    if not graphify_bin:
        print("graph_enrich: 'graphify' not found on PATH -- skipping "
              "(pip install graphifyy, or uv tool install graphifyy)")
        return None
    cmd = [graphify_bin, "extract", str(target), "--backend", backend,
           "--out", str(out_dir), "--no-cluster"]
    for pattern in (excludes or GRAPHIFY_EXCLUDES):
        cmd += ["--exclude", pattern]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print(f"graph_enrich: graphify extract failed ({proc.returncode}):\n{proc.stderr}")
        return None
    result_path = Path(out_dir) / "graphify-out" / "graph.json"
    if not result_path.is_file():
        print(f"graph_enrich: expected output missing at {result_path}")
        return None
    return result_path


def write_inferred_edges(edges, out_path, min_confidence):
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "source": "scripts/graph_enrich.py (graphify extract, INFERRED edges only)",
        "min_confidence": min_confidence,
        "edges": edges,
    }
    fd, tmp = tempfile.mkstemp(dir=str(out_path.parent), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, out_path)


def main():
    parser = argparse.ArgumentParser(
        description="Scoped graphify pass -> high-confidence INFERRED concept "
                     "edges merged into graph.json by graph_builder.py (spec §10)")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--vault", default=str(DEFAULT_VAULT))
    parser.add_argument("--graph", default=str(DEFAULT_GRAPH))
    parser.add_argument("--skills", default=str(DEFAULT_SKILLS))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--backend", default="gemini")
    parser.add_argument("--min-confidence", type=float, default=MIN_CONFIDENCE)
    args = parser.parse_args()

    if not os.path.isfile(args.graph):
        sys.exit(f"canonical graph not found: {args.graph}")
    with open(args.graph, "r", encoding="utf-8") as f:
        canonical_graph = json.load(f)

    skills_file_map = load_skills_file_map(args.skills)
    if skills_file_map is None:
        print(f"graph_enrich: skills repo not reachable at {args.skills} -- "
              "skill-id mapping will be skipped this run")

    with tempfile.TemporaryDirectory(prefix="graph_enrich_") as tmp:
        raw_path = run_graphify_extract(args.repo_root, tmp, backend=args.backend)
        if raw_path is None:
            print("graph_enrich: no extraction produced -- leaving existing "
                  "graph_inferred_edges.json (if any) untouched")
            return 0
        with open(raw_path, "r", encoding="utf-8") as f:
            raw_extraction = json.load(f)

        edges = extract_inferred_edges(raw_extraction, canonical_graph, args.vault,
                                        skills_file_map, args.min_confidence)

    write_inferred_edges(edges, args.out, args.min_confidence)
    print(f"graph_enrich: wrote {len(edges)} inferred edges -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/test_graph_enrich.py -v`
Expected: PASS, all cases.

- [ ] **Step 5: Commit**

```bash
git add scripts/graph_enrich.py tests/test_graph_enrich.py
git commit -m "feat(graph-brain): add scripts/graph_enrich.py scoped graphify pass (spec §10)"
```

---

### Task 3: `mcp_bridge.py` — `inferred` edge type at reduced weight

**Files:**
- Modify: `.agents/mcp-bridge/mcp_bridge.py:38-43` (constants block), `.agents/mcp-bridge/mcp_bridge.py:205-239` (`related_nodes()` adjacency + scoring)
- Test: `tests/test_bridge_inferred_edges.py` (new)

**Interfaces:**
- Produces: `mcp_bridge.EDGE_TYPE_WEIGHT: dict[str, float]` module constant (`{"wikilink": 1.0, "mentions": 1.0, "skill-link": 1.0, "inferred": <env-overridable, default 0.5>}`).
- Consumes: edges of `type == "inferred"` as written by Task 1's merge step; no other dependency on Tasks 1/2.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_bridge_inferred_edges.py
"""related_nodes() §10 -- "inferred" edge type weighted below
wikilink/mentions/skill-link; graphs with no inferred edges at all must be
unaffected by this change (regression guard)."""
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


# seed 's' reaches both 'wiki_hit' (via wikilink) and 'inferred_hit' (via
# inferred) at the SAME hop with IDENTICAL centrality -- only the edge-type
# weight can separate their rank.
_GRAPH = {
    "meta": {"version": 5},
    "nodes": [
        {"id": "s", "layer": "note", "path": "s.md", "centrality_global": 0.1},
        {"id": "wiki_hit", "layer": "note", "path": "wiki_hit.md", "centrality_global": 0.1},
        {"id": "inferred_hit", "layer": "note", "path": "inferred_hit.md", "centrality_global": 0.1},
    ],
    "edges": [
        {"from": "s", "to": "wiki_hit", "type": "wikilink"},
        {"from": "s", "to": "inferred_hit", "type": "inferred", "confidence_score": 0.9},
    ],
    "issues": [],
}


def test_inferred_edge_ranks_below_wikilink_edge_at_equal_centrality(tmp_path):
    b = _bridge(tmp_path, _GRAPH)
    out_ids = [n["id"] for n in b.related_nodes(["s"], limit=5)]
    assert "wiki_hit" in out_ids
    assert "inferred_hit" in out_ids
    assert out_ids.index("wiki_hit") < out_ids.index("inferred_hit")


def test_inferred_edge_not_traversed_when_weight_set_to_zero(monkeypatch, tmp_path):
    monkeypatch.setitem(mcp_bridge.EDGE_TYPE_WEIGHT, "inferred", 0.0)
    b = _bridge(tmp_path, _GRAPH)
    out_ids = [n["id"] for n in b.related_nodes(["s"], limit=5)]
    assert "inferred_hit" not in out_ids
    assert "wiki_hit" in out_ids


def test_edge_type_outside_allow_list_is_still_ignored(tmp_path):
    graph = json.loads(json.dumps(_GRAPH))
    graph["edges"].append({"from": "s", "to": "import_only", "type": "import"})
    graph["nodes"].append({"id": "import_only", "layer": "monolith", "centrality_global": 0.1})
    b = _bridge(tmp_path, graph)
    out_ids = [n["id"] for n in b.related_nodes(["s"], limit=5)]
    assert "import_only" not in out_ids
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/test_bridge_inferred_edges.py -v`
Expected: FAIL — `AttributeError: module 'mcp_bridge' has no attribute 'EDGE_TYPE_WEIGHT'`.

- [ ] **Step 3: Implement the weighted allow-list**

Add this constant in `mcp_bridge.py` right after the existing `GRAPH_ROUTE_COMMUNITY_BONUS` line (end of the v5 constants block, ~line 42):

```python
# §10 -- graphify-sourced inferred concept edges (optional; a graph with no
# "inferred" edges is unaffected). Weighted below the three explicit layers
# so an LLM guess never outranks a real wikilink/mentions/skill-link link.
EDGE_TYPE_WEIGHT = {
    "wikilink": 1.0, "mentions": 1.0, "skill-link": 1.0,
    "inferred": float(os.environ.get("GRAPH_INFERRED_EDGE_WEIGHT", "0.5")),
}
```

Replace the adjacency-building block inside `related_nodes()` (currently `adjacency: Dict[str, set] = {}` through the `for e in graph.get("edges", []): ...` loop):

```python
        adjacency: Dict[str, Dict[str, float]] = {}
        for e in graph.get("edges", []):
            etype = e.get("type")
            if etype not in EDGE_TYPE_WEIGHT:
                continue
            w = EDGE_TYPE_WEIGHT[etype]
            a, b = e.get("from"), e.get("to")
            if w > adjacency.setdefault(a, {}).get(b, 0.0):
                adjacency[a][b] = w
            if w > adjacency.setdefault(b, {}).get(a, 0.0):
                adjacency[b][a] = w
```

Replace the hop-loop body (`for nid in frontier: for nb in adjacency.get(nid, ()): ...`) so it reads the per-edge weight:

```python
        for _ in range(hops):
            nxt: set = set()
            for nid in frontier:
                for nb, edge_w in adjacency.get(nid, {}).items():
                    if nb in visited or nb not in nodes:
                        continue
                    score = weight * edge_w * (1 + _cent(nodes[nb]))
                    if nodes[nb].get("community") in seed_comms:
                        score *= GRAPH_COMMUNITY_BONUS
                    if score > scored.get(nb, 0.0):
                        scored[nb] = score
                    nxt.add(nb)
            visited |= nxt
            frontier = nxt
            weight *= decay
```

(The rest of `related_nodes()` — the community-seeded expansion and final ranking — is untouched; `wikilink`/`mentions`/`skill-link` all keep weight `1.0`, so existing scores are bit-for-bit identical when no `inferred` edges are present.)

- [ ] **Step 4: Run tests to verify they pass, plus the full existing regression suite**

Run: `python -m pytest tests/test_bridge_inferred_edges.py tests/test_bridge_community_scoring.py tests/test_retrieval_regression.py -v`
Expected: PASS, all three files — the two pre-existing files must show **zero** changed assertions, confirming the weighted-adjacency rewrite is behavior-preserving for graphs with no `inferred` edges.

- [ ] **Step 5: Commit**

```bash
git add .agents/mcp-bridge/mcp_bridge.py tests/test_bridge_inferred_edges.py
git commit -m "feat(graph-brain): weight inferred edges below wikilink/mentions/skill-link in mcp_bridge (spec §10)"
```

---

### Task 4: Documentation + spec status update

**Files:**
- Modify: `CLAUDE.md` (Graph Brain section)
- Modify: `docs/superpowers/specs/2026-09-02-graph-brain-v5-communities-design.md` (§10 heading only)

**Interfaces:** none (docs-only task; no code consumes or produces anything here).

- [ ] **Step 1: Update `CLAUDE.md`'s Graph Brain section**

In the `## 🕸️ Graph Brain` section of `CLAUDE.md`, directly below the existing "Deferred: graphify LLM-inferred concept edges..." line, replace that line with:

```markdown
**Inferred-edges layer (§10, implemented 2026-10-01):** `python scripts/graph_enrich.py`
runs a scoped `graphify extract` pass (vault `.md` + tracked Brain `.py` + skills
registry; excludes `.obsidian/`, `node_modules/`, `brain-bundle*`,
`openhuman-build/`, minified JS) and writes high-confidence (`>=0.7`) `INFERRED`
concept edges to `06-AI-Context/graph_inferred_edges.json`. `graph_builder.py`
merges that file in as an optional `{type:"inferred"}` layer (file absent =
no-op); `mcp_bridge.py`'s `related_nodes()` traverses it at a lower weight than
`wikilink`/`mentions`/`skill-link` (`EDGE_TYPE_WEIGHT`, env `GRAPH_INFERRED_EDGE_WEIGHT`).
Host/CI only, manual invocation — **not** wired into `.github/workflows/graph-refresh.yml`
yet; requires `graphify` on PATH (`uv tool install graphifyy`) plus a backend API key
(`GEMINI_API_KEY` by default). Communities + centrality (`communities.py`) are
untouched by this layer — it stays native, per spec.
```

- [ ] **Step 2: Mark §10 implemented in the spec**

In `docs/superpowers/specs/2026-09-02-graph-brain-v5-communities-design.md`, directly below the `## 10. Deferred increment — graphify LLM-inferred concept edges (NOT this spec)` heading, add:

```markdown
> **Status: implemented 2026-10-01.** See `scripts/graph_enrich.py`,
> `graph_builder.py::load_inferred_edges()`, and `mcp_bridge.py::EDGE_TYPE_WEIGHT`.
> Not yet run against the real vault/production graph — see the open follow-up
> at the end of this plan (`docs/superpowers/plans/2026-10-01-graph-brain-inferred-edges.md`)
> before picking real `retrieval_cases.json` "should-connect" pairs for §11 Q3.
```

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md "docs/superpowers/specs/2026-09-02-graph-brain-v5-communities-design.md"
git commit -m "docs(graph-brain): record §10 inferred-edges layer as implemented"
```

---

## Open follow-up (explicitly NOT a task in this plan)

Spec §11 open question #3 asks for "final `retrieval_cases.json` set — chosen against the real vault during implementation with Lyndz's input on which 'should-connect' pairs matter." This plan does **not** fabricate those cases. Once Task 2 ships, the next step (separate from this plan) is:

1. Run `python scripts/graph_enrich.py` against the real repo (needs `GEMINI_API_KEY` or another backend key set, and `graphify`/`graphifyy` installed — confirmed present via `uv tool list` on this host already).
2. Inspect the resulting `HYPERFOCUS_ZONE/06-AI-Context/graph_inferred_edges.json` with Lyndz.
3. Hand-pick 1-2 new "gap" cases for `tests/fixtures/retrieval_cases.json` the same way the existing `difficulty_dial` gap cases were chosen (per `tests/test_retrieval_regression.py` / `task-6-report.md` convention) — pairs only the inferred layer can surface, verified against `tests/fixtures/graph_v5_snapshot.json` plus a refreshed snapshot that includes real inferred edges.
4. Decide — with Lyndz, not unilaterally — whether to wire `graph_enrich.py` into `.github/workflows/graph-refresh.yml` for periodic auto-refresh, given it costs LLM tokens on every run (unlike the free, stdlib-only `graph_builder.py` refresh that workflow already does).
