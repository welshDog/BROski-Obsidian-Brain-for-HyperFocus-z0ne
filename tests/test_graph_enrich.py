"""scripts/graph_enrich.py -- ID mapping, confidence filter, dedup (spec §10).
No network/API calls: run_graphify_extract() is exercised only through a
subprocess.run / shutil.which stub that checks the CLI invocation shape."""
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))

import graph_enrich  # noqa: E402

VAULT = "/vault"
REPO_ROOT = "/repo"

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
        "/vault/01-Projects/Alpha.md", VAULT, REPO_ROOT) == "note:Alpha"


def test_md_outside_vault_is_unmapped():
    assert graph_enrich.vault_relative_md_id("/elsewhere/Alpha.md", VAULT, REPO_ROOT) is None


def test_non_md_is_unmapped_by_note_mapper():
    assert graph_enrich.vault_relative_md_id("/vault/foo.py", VAULT, REPO_ROOT) is None


def test_vault_relative_md_id_anchors_relative_path_to_repo_root_not_cwd(tmp_path, monkeypatch):
    """Regression: graphify emits source_file relative to the scanned corpus
    root, not absolute. Resolving a relative source_file against
    Path.cwd() (the pre-fix behavior) silently maps every note to None
    whenever graph_enrich.py is invoked from any directory other than
    repo_root -- and a mapping failure means write_inferred_edges() happily
    overwrites a previously-good sidecar with an empty edge list. Anchoring
    to the passed-in repo_root instead of the process CWD must make this
    independent of where the script is launched from."""
    monkeypatch.chdir(tmp_path)  # CWD is now unrelated to repo_root/vault_root
    repo_root = "/myrepo"
    vault_root = "/myrepo/HYPERFOCUS_ZONE"
    assert graph_enrich.vault_relative_md_id(
        "HYPERFOCUS_ZONE/02-Areas/Foo.md", vault_root, repo_root) == "note:Foo"


def test_vault_relative_md_id_relative_path_outside_vault_is_unmapped(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    repo_root = "/myrepo"
    vault_root = "/myrepo/HYPERFOCUS_ZONE"
    assert graph_enrich.vault_relative_md_id(
        "docs/Foo.md", vault_root, repo_root) is None


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
    out = graph_enrich.extract_inferred_edges(raw, CANONICAL, VAULT, REPO_ROOT, None, 0.7)
    assert out == [{"from": "note:Gamma", "to": "hyper_brain_core",
                     "relation": "conceptually_related_to", "confidence_score": 0.85}]


def test_extract_inferred_edges_maps_relative_source_files_via_repo_root():
    """Regression for the CWD-anchoring bug: graphify's real output uses
    paths relative to the scanned corpus root, not absolute paths."""
    raw = {
        "nodes": [
            {"id": "a", "source_file": "HYPERFOCUS_ZONE/02-Areas/Gamma.md"},
            {"id": "b", "source_file": "hyper_brain_core.py"},
        ],
        "edges": [_raw_edge("a", "b", score=0.85)],
    }
    canonical = {
        "nodes": [{"id": "hyper_brain_core", "layer": "monolith"}],
        "edges": [],
    }
    out = graph_enrich.extract_inferred_edges(
        raw, canonical, "/myrepo/HYPERFOCUS_ZONE", "/myrepo", None, 0.7)
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
    assert graph_enrich.extract_inferred_edges(raw, CANONICAL, VAULT, REPO_ROOT, None, 0.7) == []


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
    assert graph_enrich.extract_inferred_edges(raw, CANONICAL, VAULT, REPO_ROOT, None, 0.7) == []


def test_extract_inferred_edges_drops_unmappable_endpoint():
    raw = {
        "nodes": [
            {"id": "a", "source_file": "/vault/02-Areas/Gamma.md"},
            {"id": "b", "source_file": "/repo/scripts/stale_mirror_script.py"},
        ],
        "edges": [_raw_edge("a", "b")],
    }
    assert graph_enrich.extract_inferred_edges(raw, CANONICAL, VAULT, REPO_ROOT, None, 0.7) == []


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
    assert graph_enrich.extract_inferred_edges(raw, CANONICAL, VAULT, REPO_ROOT, None, 0.7) == []


def test_extract_inferred_edges_dedupes_against_existing_wikilink():
    raw = {
        "nodes": [
            {"id": "a", "source_file": "/vault/01-Projects/Alpha.md"},
            {"id": "b", "source_file": "/vault/01-Projects/Beta.md"},
        ],
        "edges": [_raw_edge("a", "b")],
    }
    assert graph_enrich.extract_inferred_edges(raw, CANONICAL, VAULT, REPO_ROOT, None, 0.7) == []


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
    out = graph_enrich.extract_inferred_edges(raw, CANONICAL, VAULT, REPO_ROOT, None, 0.7)
    assert len(out) == 1
    assert out[0]["confidence_score"] == 0.9
    assert out[0]["relation"] == "strong_link"


def test_merge_raw_extractions_combines_nodes_and_edges():
    a = {"nodes": [{"id": "a"}], "edges": [{"source": "a", "target": "b"}]}
    b = {"nodes": [{"id": "b"}], "edges": [{"source": "b", "target": "c"}]}
    merged = graph_enrich.merge_raw_extractions(a, b)
    assert merged["nodes"] == [{"id": "a"}, {"id": "b"}]
    assert merged["edges"] == [{"source": "a", "target": "b"}, {"source": "b", "target": "c"}]


def test_merge_raw_extractions_skips_none():
    a = {"nodes": [{"id": "a"}], "edges": []}
    merged = graph_enrich.merge_raw_extractions(a, None)
    assert merged["nodes"] == [{"id": "a"}]


def test_graphify_excludes_cover_non_mappable_repo_dirs():
    """scripts/ holds stale mirror copies of tracked modules (CLAUDE.md:
    'Dead code identified: scripts/ (stale mirror)') -- code_module_id()
    matches by bare filename stem regardless of directory, so a stale
    scripts/hyper_brain_core.py would otherwise be misattributed to the
    canonical hyper_brain_core node. docs/, tests/, .superpowers/, .claude/
    and .github/ can never map to any canonical id and are pure LLM-token
    waste to scan."""
    for pattern in ("scripts/", "docs/", "tests/", ".superpowers/", ".claude/", ".github/"):
        assert pattern in graph_enrich.GRAPHIFY_EXCLUDES


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
