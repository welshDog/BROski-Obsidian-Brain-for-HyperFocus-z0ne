"""Integration: graph_builder.py stamps v5 community fields, fail-open on error."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import communities  # noqa: E402  (ensure it's in sys.modules for the Ruling-1 test)
import graph_builder  # noqa: E402

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
        # fixture partition: {hyper_brain_core, note:Alpha}, {note:Beta, note:Gamma}, {note:Delta}
        assert graph["meta"]["communities_count"] == 3
        for n in graph["nodes"]:
            assert "community" in n
            assert "community_label" in n
            assert isinstance(n["centrality_global"], float)
        by_id = {n["id"]: n for n in graph["nodes"]}
        # NOTE: the retrieval topology includes cross-layer `mentions` edges, so
        # Alpha's mention of hyper_brain_core pulls it into that code node's
        # community; CNM then stops at its first local optimum, leaving
        # Beta+Gamma as a separate pair. Community id == smallest member id.
        # (The brief's Step-1 comment predicted Alpha<->Beta<->Gamma as one
        # community; verified against the real communities.py that is not the
        # partition — see task-3-report.md.)
        assert by_id["note:Beta"]["community"] == by_id["note:Gamma"]["community"]
        assert by_id["note:Alpha"]["community"] == by_id["hyper_brain_core"]["community"]
        assert by_id["note:Alpha"]["community"] == "hyper_brain_core"   # min member id
        assert by_id["note:Delta"]["community"] == "note:Delta"         # isolated singleton


def _boom(*args, **kwargs):
    raise RuntimeError("boom")


def test_fail_open_when_communities_module_raises(monkeypatch, capsys):
    """Ruling 1: the brief's PYTHONPATH-shadowing subprocess test cannot work
    (sys.path[0] is the script dir, which wins over PYTHONPATH). Instead call
    merge() directly with communities.pagerank patched to raise. The stamp
    block's `from communities import pagerank` re-does getattr on
    sys.modules['communities'] at call time, so the patched name is bound."""
    monkeypatch.setattr("communities.pagerank", _boom)
    graph = {
        "meta": {},
        "nodes": [
            # layer "code" so merge()'s kept_nodes filter retains it — a "note"
            # node would be dropped (rebuilt from the []'s passed) and the
            # per-node absence loop below would run over an empty list.
            {"id": "x", "layer": "code", "path": "x.py", "centrality": 0, "status": "live"}
        ],
        "edges": [],
        "issues": [],
    }
    out = graph_builder.merge(
        graph, [], [], [], 0, skill_nodes=[], skill_edges=[]
    )
    captured = capsys.readouterr()
    assert "communities: skipped" in captured.out
    assert out["meta"]["version"] == 4
    assert out["nodes"]  # guard: the absence loop below must not be vacuous
    for n in out["nodes"]:
        assert "community" not in n
        assert "community_label" not in n
        assert "centrality_global" not in n


def test_fail_open_strips_stale_v5_fields_from_preserved_nodes(monkeypatch, capsys):
    """Merge-blocker regression: on a real run the loaded graph IS the previously
    committed v5 graph.json, so preserved code-layer nodes already carry the prior
    run's community fields. A communities.py failure must strip them — otherwise a
    graph stamped version:4 still ships stale per-node community data that
    mcp_bridge keys on (spec §5.5 / §7.4)."""
    monkeypatch.setattr("communities.pagerank", _boom)
    graph = {
        # simulate the previously-committed v5 graph being reloaded
        "meta": {
            "version": 5,
            "layers": ["code", "notes", "mentions", "skills", "communities"],
            "communities_count": 7,
            "community_algo": "greedy-modularity",
        },
        "nodes": [
            {"id": "x", "layer": "code", "path": "x.py", "centrality": 0,
             "status": "live", "community": "STALE",
             "community_label": "stale label", "centrality_global": 0.123},
        ],
        "edges": [],
        "issues": [],
    }
    out = graph_builder.merge(
        graph, [], [], [], 0, skill_nodes=[], skill_edges=[]
    )
    captured = capsys.readouterr()
    assert "communities: skipped" in captured.out
    assert out["meta"]["version"] == 4
    assert "communities" not in out["meta"].get("layers", [])
    assert "communities_count" not in out["meta"]
    assert "community_algo" not in out["meta"]
    assert out["nodes"]  # guard: the absence loop must not be vacuous
    for n in out["nodes"]:
        assert "community" not in n
        assert "community_label" not in n
        assert "centrality_global" not in n
