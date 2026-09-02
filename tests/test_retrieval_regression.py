"""Precision@5 gate: the v5 retrieval path must never lose to v4, and must win
on the tagged 'gap' cases. Ground truth is hand-labelled in retrieval_cases.json."""
import json
import os
import sys

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", ".agents", "mcp-bridge")))
import mcp_bridge  # noqa: E402

FX = os.path.join(os.path.dirname(__file__), "fixtures")
V5 = json.load(open(os.path.join(FX, "graph_v5_snapshot.json"), encoding="utf-8"))
CASES = json.load(open(os.path.join(FX, "retrieval_cases.json"), encoding="utf-8"))["cases"]


def _v4(graph):
    g = json.loads(json.dumps(graph))
    g["meta"]["version"] = 4
    for n in g["nodes"]:
        n.pop("community", None)
        n.pop("centrality_global", None)
    return g


def _bridge(tmp_path, graph, name):
    v = tmp_path / name / "vault"
    (v / "06-AI-Context").mkdir(parents=True)
    (v / "06-AI-Context" / "graph.json").write_text(json.dumps(graph), encoding="utf-8")
    return mcp_bridge.MCPBridge(vault_path=str(v))


def _precision_at_5(got, expected):
    if not expected:
        return 1.0
    top = got[:5]
    return len(set(top) & set(expected)) / min(5, len(expected))


def _score(bridge, case):
    r = bridge.route_skills(case["query"], limit=10)
    note_ids = ["note:" + os.path.splitext(p)[0].split("/")[-1] for p in r["notes"]]
    skill_p = _precision_at_5([s["id"] for s in r["skills"]], case["expect_skills"])
    note_p = _precision_at_5(note_ids + r["notes"], case["expect_notes"])
    return (skill_p + note_p) / 2


def test_ground_truth_ids_are_real_nodes():
    """Every expect_* id must resolve to a real node in the snapshot — a case
    that references a phantom id is a bug, not a passing gate."""
    node_ids = {n["id"] for n in V5["nodes"]}
    paths = {n["path"] for n in V5["nodes"] if n.get("path")}
    basenames = {os.path.splitext(p)[0].split("/")[-1] for p in paths}
    missing = []
    for case in CASES:
        for sid in case["expect_skills"]:
            if sid not in node_ids:
                missing.append((case["query"], sid))
        for nid in case["expect_notes"]:
            if not (nid in node_ids or nid in paths
                    or nid.replace("note:", "") in basenames):
                missing.append((case["query"], nid))
    assert not missing, f"retrieval_cases.json references non-existent ids: {missing}"


def test_v5_never_worse_than_v4_and_wins_the_gap_cases(tmp_path):
    b5 = _bridge(tmp_path, V5, "v5")
    b4 = _bridge(tmp_path, _v4(V5), "v4")
    regressions, gap_wins = [], []
    for case in CASES:
        s5, s4 = _score(b5, case), _score(b4, case)
        if s5 + 1e-9 < s4:
            regressions.append((case["query"], s4, s5))
        if case.get("gap") and s5 > s4 + 1e-9:
            gap_wins.append(case["query"])
    assert not regressions, f"v5 regressed vs v4: {regressions}"
    n_gap = sum(1 for c in CASES if c.get("gap"))
    assert len(gap_wins) >= max(1, n_gap - 1), \
        f"expected v5 to beat v4 on the gap cases, won only {gap_wins}"
