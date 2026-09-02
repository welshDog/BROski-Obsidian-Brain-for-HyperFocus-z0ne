"""related_nodes() / route_skills() community-aware scoring, + v4 fail-open parity."""
import inspect
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
# NO edge path. 'far' is in a DIFFERENT community and has no edge path.
# centrality_global values per Ruling 2: sum == 1.0 (realistic PageRank).
# n_count = 4, so _cent = centrality_global * 4:
#   comm_hit -> 0.36 * 4 = 1.44  >= GRAPH_COMMUNITY_SEED_FLOOR (1.0)  -> surfaced
#   far      -> 0.30 * 4 = 1.20  >= 1.0 too, so 'far' clears the floor and the
#              ONLY thing keeping it out of the results is its different community
#              ("far" not in seed_comms == {"s"}) — this unmasks the negative control.
_V5 = {
    "meta": {"version": 5},
    "nodes": [
        {"id": "s",        "layer": "note", "path": "s.md",        "community": "s", "centrality_global": 0.16},
        {"id": "edge_hit", "layer": "note", "path": "edge_hit.md", "community": "s", "centrality_global": 0.18},
        {"id": "comm_hit", "layer": "note", "path": "comm_hit.md", "community": "s", "centrality_global": 0.36},
        {"id": "far",      "layer": "note", "path": "far.md",      "community": "far", "centrality_global": 0.30},
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


# ─── Task 5: route_skills() same-community bonus + community_members() ──────────
#
# Fixture: query "focus tracker" token-hits 'focus_engine' (score 2) and the
# same-community skill 'skill:HS-900' (score 1, via its "focus" category). The
# foreign-community skill 'skill:HS-777' has ZERO token hits (title/desc/category
# share no >3-char substring with "focus"/"tracker"), so it is NOT a seed — it is
# pulled into skill_rank only by its skill-link edge to 'focus_engine'. That keeps
# seed_comms == {"focus"} clean, so HS-777 is a true negative control for the bonus.
_V5_ROUTE = {
    "meta": {"version": 5},
    "nodes": [
        {"id": "focus_engine", "layer": "engine", "path": "focus_engine.py",
         "community": "focus", "centrality_global": 0.02},
        {"id": "skill:HS-900", "layer": "skill", "title": "Deep Work",
         "description": "quiet mode", "category": "focus",
         "community": "focus", "centrality_global": 0.01},
        {"id": "skill:HS-777", "layer": "skill", "title": "Web Deploy",
         "description": "ship it", "category": "web",
         "community": "other", "centrality_global": 0.01},
    ],
    "edges": [{"from": "focus_engine", "to": "skill:HS-777", "type": "skill-link"}],
    "issues": [],
}


def test_route_skills_boosts_same_community_skill_without_edge(tmp_path, monkeypatch):
    """A skill sharing a seed's community gains exactly GRAPH_ROUTE_COMMUNITY_BONUS
    on its rank, even with no skill-link edge to any seed; a foreign-community
    skill pulled in only by an edge is untouched."""
    b = _bridge(tmp_path, _V5_ROUTE)

    def _scores(bonus):
        monkeypatch.setattr(mcp_bridge, "GRAPH_ROUTE_COMMUNITY_BONUS", bonus)
        out = b.route_skills("focus tracker", limit=5)
        return {s["id"]: s["score"] for s in out["skills"]}

    base = _scores(0.0)
    boosted = _scores(5.0)
    assert "skill:HS-900" in base and "skill:HS-777" in base
    assert boosted["skill:HS-900"] == base["skill:HS-900"] + 5.0   # same community → boosted
    assert boosted["skill:HS-777"] == base["skill:HS-777"]         # foreign community → untouched


def test_route_skills_return_shape_unchanged(tmp_path):
    """Guard: the bonus only re-ranks — it adds no keys to the /route contract."""
    b = _bridge(tmp_path, _V5_ROUTE)
    out = b.route_skills("focus tracker", limit=3)
    assert set(out.keys()) == {"query", "seeds", "skills", "notes", "code"}


def test_route_skills_v4_graph_applies_no_bonus(tmp_path, monkeypatch):
    """Guard / fail-open: on a v4 graph seed_comms is empty, so the bonus never
    fires and the ranking is independent of GRAPH_ROUTE_COMMUNITY_BONUS."""
    b = _bridge(tmp_path, _v4(_V5_ROUTE))

    def _scores(bonus):
        monkeypatch.setattr(mcp_bridge, "GRAPH_ROUTE_COMMUNITY_BONUS", bonus)
        out = b.route_skills("focus tracker", limit=5)
        return {s["id"]: s["score"] for s in out["skills"]}

    assert _scores(0.0) == _scores(99.0)


def test_community_members_orders_by_centrality_desc(tmp_path):
    b = _bridge(tmp_path, _V5)
    # community "s" holds s/edge_hit/comm_hit; sorted by centrality_global desc,
    # 's' itself excluded, 'far' (community "far") excluded.
    assert b.community_members("s") == ["comm_hit", "edge_hit"]
    assert b.community_members("s", limit=1) == ["comm_hit"]


def test_community_members_respects_exclude(tmp_path):
    b = _bridge(tmp_path, _V5)
    assert b.community_members("s", exclude={"comm_hit"}) == ["edge_hit"]


def test_community_members_v4_graph_returns_empty(tmp_path):
    b = _bridge(tmp_path, _v4(_V5))
    assert b.community_members("s") == []


def test_community_members_unknown_or_uncommunitied_node_returns_empty(tmp_path):
    g = json.loads(json.dumps(_V5))
    g["nodes"].append({"id": "orphan", "layer": "note", "path": "orphan.md"})
    b = _bridge(tmp_path, g)
    assert b.community_members("does-not-exist") == []
    assert b.community_members("orphan") == []


def test_community_members_missing_graph_returns_empty(tmp_path):
    b = mcp_bridge.MCPBridge(vault_path=str(tmp_path / "no-such-vault"))
    assert b.community_members("s") == []


def test_graph_related_endpoint_wires_related_by_community():
    """Ruling 3: the __main__ app block isn't import-friendly — assert the
    endpoint source wires community_members() into a related_by_community key."""
    src = inspect.getsource(mcp_bridge)
    assert "_bridge.community_members(" in src
    assert '"related_by_community"' in src
