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
# centrality_global values per Ruling 2: sum ~= 1.0 (realistic PageRank) and
# comm_hit's _cent (= centrality_global * n_count, n_count=4) = 0.38 * 4 = 1.52,
# comfortably >= the default GRAPH_COMMUNITY_SEED_FLOOR of 1.0 so the
# default-path community-seeding tests surface comm_hit.
_V5 = {
    "meta": {"version": 5},
    "nodes": [
        {"id": "s",        "layer": "note", "path": "s.md",        "community": "s", "centrality_global": 0.20},
        {"id": "edge_hit", "layer": "note", "path": "edge_hit.md", "community": "s", "centrality_global": 0.22},
        {"id": "comm_hit", "layer": "note", "path": "comm_hit.md", "community": "s", "centrality_global": 0.38},
        {"id": "far",      "layer": "note", "path": "far.md",      "community": "far", "centrality_global": 0.20},
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
    assert "far" not in out_ids                         # negative control: different community, no edge path


def test_v4_graph_output_is_identical_to_legacy_ranker(tmp_path):
    b5 = _bridge(tmp_path / "a", _V5)
    b4 = _bridge(tmp_path / "b", _v4(_V5))
    # v5 path still ranks the edge hit first (sanity — same fixture, v5 graph)
    assert [n["id"] for n in b5.related_nodes(["s"], limit=5)][0] == "edge_hit"
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
