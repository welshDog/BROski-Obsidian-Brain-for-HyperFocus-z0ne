"""P2-2 — Brain Constellation (Level 20) tests.

Covers the graph builder (pure) + the Obsidian Canvas generator (writes a valid
JSON Canvas to a temp vault). The live :8100 endpoints just call these.
"""

import asyncio
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from constellation_builder import ConstellationBuilder  # noqa: E402

SAMPLE = {
    "generated_at": "2026-06-20T00:00:00Z",
    "system": {"status": "ok", "level": "20/20", "completion_pct": 100, "services_online": "5/6"},
    "engine": {"container": 30, "port": 8100, "modules": ["hyper_brain_core", "focus_tracker", "difficulty_dial"]},
    "focus": {"active": True, "intent": "build the constellation"},
    "economy": {"broski_coins_7d": 100, "xp_7d": 200, "sessions_7d": 5,
                "current_streak": 3, "longest_streak": 7, "recovery_tokens": 1},
    "vault": ["00-Inbox", "Hub"],
    "ecosystem_repos": ["HyperCode-V2.4", "BROski-Obsidian-Brain", "Hyper-Vibe-Coding-Course"],
}


def _builder():
    return ConstellationBuilder(vault_path=tempfile.mkdtemp())


def test_graph_has_core_nodes():
    g = _builder().build_graph(SAMPLE)
    ids = {n["id"] for n in g["nodes"]}
    assert "zone" in ids and "engine" in ids and "economy" in ids and "vault" in ids
    assert "module:hyper_brain_core" in ids
    assert "repo:HyperCode-V2.4" in ids


def test_graph_edges_wire_engine_and_repos():
    g = _builder().build_graph(SAMPLE)
    pairs = {(e["source"], e["target"]) for e in g["edges"]}
    assert ("zone", "engine") in pairs
    assert ("engine", "module:focus_tracker") in pairs
    assert ("zone", "repo:HyperCode-V2.4") in pairs
    # real cross-repo wiring (Course -> V2.4 manifest)
    assert ("repo:Hyper-Vibe-Coding-Course", "repo:HyperCode-V2.4") in pairs


def test_graph_counts_match():
    g = _builder().build_graph(SAMPLE)
    assert g["counts"]["nodes"] == len(g["nodes"])
    assert g["counts"]["edges"] == len(g["edges"])


def test_canvas_is_valid_obsidian_json():
    b = _builder()
    g = b.build_graph(SAMPLE)
    path = asyncio.run(b.write_canvas(g))
    assert path.endswith("Brain-Constellation.canvas")
    with open(path, "r", encoding="utf-8") as f:
        canvas = json.load(f)
    assert "nodes" in canvas and "edges" in canvas
    # every node has the required Obsidian Canvas fields
    for n in canvas["nodes"]:
        assert all(k in n for k in ("id", "type", "x", "y", "width", "height"))
    # every edge references real nodes
    node_ids = {n["id"] for n in canvas["nodes"]}
    for e in canvas["edges"]:
        assert e["fromNode"] in node_ids and e["toNode"] in node_ids
    # node count parity with the graph
    assert len(canvas["nodes"]) == g["counts"]["nodes"]


def test_canvas_has_no_orange():
    b = _builder()
    g = b.build_graph(SAMPLE)
    path = asyncio.run(b.write_canvas(g))
    with open(path, "r", encoding="utf-8") as f:
        canvas = json.load(f)
    # "2" is the orange preset — banned by the HFZ brand rule.
    assert all(n.get("color") != "2" for n in canvas["nodes"])
