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
