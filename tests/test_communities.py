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
