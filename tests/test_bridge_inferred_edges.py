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
