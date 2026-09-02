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
