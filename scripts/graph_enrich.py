#!/usr/bin/env python3
"""
scripts/graph_enrich.py
Graph Brain v5 §10 -- deferred increment.

Runs a SCOPED graphify pass over the vault (*.md), the Brain's own tracked
Python modules, and the HYPER-SILLs skills registry, excluding Obsidian
plugin bundles, node_modules, brain-bundle mirrors, openhuman-build, and
minified JS. Extracts only high-confidence INFERRED concept edges, remaps
both endpoints to canonical graph.json node ids, drops anything that
duplicates an existing wikilink/mentions/skill-link edge or fails to map,
and atomically writes the survivors to graph_inferred_edges.json.

graph_builder.py optionally merges that file in as an {"type": "inferred"}
edge layer (file absent = no-op). Communities/PageRank (communities.py)
never see this layer -- it stays native, per spec §10.

Host/CI only. This is the one script in the repo allowed to depend on a
non-stdlib package (the `graphifyy` PyPI package, via its `graphify` CLI).
Requires `graphify` on PATH (`pip install graphifyy` or
`uv tool install graphifyy`) and a backend API key (ANTHROPIC_API_KEY by
default) -- missing either is a clean no-op, not a failure.

Usage:
    python scripts/graph_enrich.py
    python scripts/graph_enrich.py --backend gemini --min-confidence 0.7

BROski♾️
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_VAULT = REPO_ROOT / "HYPERFOCUS_ZONE"
DEFAULT_GRAPH = DEFAULT_VAULT / "06-AI-Context" / "graph.json"
DEFAULT_OUT = DEFAULT_VAULT / "06-AI-Context" / "graph_inferred_edges.json"
DEFAULT_SKILLS = Path(os.environ.get(
    "BRAIN_SKILLS_PATH", str(REPO_ROOT.parent / "HYPER-SILLs-By-WelshDog")))
MIN_CONFIDENCE = 0.7

GRAPHIFY_EXCLUDES = [
    ".obsidian/", "node_modules/", "brain-bundle*/", "openhuman-build/",
    "*.min.js", "scripts/", "docs/", "tests/", ".superpowers/", ".claude/",
    ".github/",
]


def vault_relative_md_id(source_file, vault_root, repo_root):
    """HYPERFOCUS_ZONE/**/Foo.md -> 'note:Foo'. None if not a .md file or
    outside the vault. graphify emits source_file RELATIVE to the scanned
    corpus root -- a relative path is anchored to repo_root, never to the
    process's current working directory (resolving against Path.cwd()
    silently mapped every note to None when this script was invoked from
    anywhere but repo_root, which then made write_inferred_edges() overwrite
    a good sidecar with an empty edge list)."""
    p = Path(source_file)
    if p.suffix.lower() != ".md":
        return None
    if not p.is_absolute():
        p = Path(repo_root) / p
    try:
        p.resolve().relative_to(Path(vault_root).resolve())
    except ValueError:
        return None
    return f"note:{p.stem}"


def code_module_id(source_file, code_ids):
    """repo/anything/hyper_brain_core.py -> 'hyper_brain_core' IFF that stem
    is already a canonical code-layer node id; else None (not a tracked
    module -- e.g. a stale scripts/ mirror or a test file)."""
    p = Path(source_file)
    if p.suffix.lower() != ".py":
        return None
    return p.stem if p.stem in code_ids else None


def skill_id_for_file(source_file, skills_file_map):
    """skills_file_map: {registry 'file' path -> HS-id}, or None when the
    skills repo was unreachable this run (preserve-mode, same convention as
    graph_builder.scan_skills)."""
    if not skills_file_map:
        return None
    norm = str(Path(source_file)).replace(os.sep, "/")
    for reg_file, sid in skills_file_map.items():
        if norm.endswith(reg_file):
            return f"skill:{sid}"
    return None


def map_to_canonical_id(source_file, vault_root, repo_root, code_ids, skills_file_map):
    if not source_file:
        return None
    return (vault_relative_md_id(source_file, vault_root, repo_root)
            or code_module_id(source_file, code_ids)
            or skill_id_for_file(source_file, skills_file_map))


def load_skills_file_map(skills_root):
    """Mirror graph_builder.scan_skills()'s reachability contract: None means
    the skills repo isn't checked out on this host. Callers must then skip
    skill-id mapping entirely -- never fabricate an empty-but-present map,
    which would read as 'registry has zero skills' instead of 'unreachable'."""
    registry_path = os.path.join(skills_root, "skills-registry.json")
    if not os.path.isfile(registry_path):
        return None
    with open(registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)
    file_map = {}
    for entry in registry.get("skills", []):
        sid = entry.get("id")
        file_ = entry.get("file")
        if sid and file_:
            file_map[file_.replace("\\", "/")] = sid
    return file_map


def extract_inferred_edges(raw_extraction, canonical_graph, vault_root, repo_root,
                            skills_file_map, min_confidence=MIN_CONFIDENCE):
    nodes_by_id = {n["id"]: n for n in raw_extraction.get("nodes", [])}
    code_ids = {n["id"] for n in canonical_graph.get("nodes", [])
                if n.get("layer") not in ("note", "skill")}
    existing_pairs = {
        frozenset((e["from"], e["to"]))
        for e in canonical_graph.get("edges", [])
        if e.get("type") in ("wikilink", "mentions", "skill-link")
    }

    best_by_pair = {}
    for e in raw_extraction.get("edges", []):
        if e.get("confidence") != "INFERRED":
            continue
        score = e.get("confidence_score") or 0.0
        if score < min_confidence:
            continue
        src_node = nodes_by_id.get(e.get("source")) or {}
        tgt_node = nodes_by_id.get(e.get("target")) or {}
        src_file = src_node.get("source_file") or e.get("source_file")
        tgt_file = tgt_node.get("source_file") or e.get("source_file")
        from_id = map_to_canonical_id(src_file, vault_root, repo_root, code_ids, skills_file_map)
        to_id = map_to_canonical_id(tgt_file, vault_root, repo_root, code_ids, skills_file_map)
        if not from_id or not to_id or from_id == to_id:
            continue
        pair = frozenset((from_id, to_id))
        if pair in existing_pairs:
            continue
        current = best_by_pair.get(pair)
        if current is None or score > current["confidence_score"]:
            best_by_pair[pair] = {
                "from": from_id, "to": to_id,
                "relation": e.get("relation"),
                "confidence_score": score,
            }
    return list(best_by_pair.values())


def merge_raw_extractions(*extractions):
    """Combine several graphify raw-extraction dicts (e.g. one pass over the
    Brain repo, one over the separate skills registry repo) into a single
    {"nodes": [...], "edges": [...]} for extract_inferred_edges(). None
    entries are skipped (a target that was unreachable or produced no
    extraction this run)."""
    nodes, edges = [], []
    for ext in extractions:
        if not ext:
            continue
        nodes.extend(ext.get("nodes", []))
        edges.extend(ext.get("edges", []))
    return {"nodes": nodes, "edges": edges}


def run_graphify_extract(target, out_dir, backend="claude", excludes=None):
    """Shell out to the headless `graphify extract` CLI. Returns the path to
    the raw extraction graph.json, or None if graphify isn't installed or
    the run failed (fail-open -- enrichment is optional, never blocks
    graph_builder.py)."""
    graphify_bin = shutil.which("graphify")
    if not graphify_bin:
        print("graph_enrich: 'graphify' not found on PATH -- skipping "
              "(pip install graphifyy, or uv tool install graphifyy)")
        return None
    cmd = [graphify_bin, "extract", str(target), "--backend", backend,
           "--out", str(out_dir), "--no-cluster"]
    for pattern in (excludes or GRAPHIFY_EXCLUDES):
        cmd += ["--exclude", pattern]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print(f"graph_enrich: graphify extract failed ({proc.returncode}):\n{proc.stderr}")
        return None
    result_path = Path(out_dir) / "graphify-out" / "graph.json"
    if not result_path.is_file():
        print(f"graph_enrich: expected output missing at {result_path}")
        return None
    return result_path


def write_inferred_edges(edges, out_path, min_confidence):
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "source": "scripts/graph_enrich.py (graphify extract, INFERRED edges only)",
        "min_confidence": min_confidence,
        "edges": edges,
    }
    fd, tmp = tempfile.mkstemp(dir=str(out_path.parent), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, out_path)


def main():
    parser = argparse.ArgumentParser(
        description="Scoped graphify pass -> high-confidence INFERRED concept "
                     "edges merged into graph.json by graph_builder.py (spec §10)")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--vault", default=str(DEFAULT_VAULT))
    parser.add_argument("--graph", default=str(DEFAULT_GRAPH))
    parser.add_argument("--skills", default=str(DEFAULT_SKILLS))
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--backend", default="claude")
    parser.add_argument("--min-confidence", type=float, default=MIN_CONFIDENCE)
    args = parser.parse_args()

    if not os.path.isfile(args.graph):
        sys.exit(f"canonical graph not found: {args.graph}")
    with open(args.graph, "r", encoding="utf-8") as f:
        canonical_graph = json.load(f)

    skills_file_map = load_skills_file_map(args.skills)
    if skills_file_map is None:
        print(f"graph_enrich: skills repo not reachable at {args.skills} -- "
              "skill-id mapping will be skipped this run")

    with tempfile.TemporaryDirectory(prefix="graph_enrich_") as tmp:
        raw_path = run_graphify_extract(args.repo_root, tmp, backend=args.backend)
        if raw_path is None:
            print("graph_enrich: no extraction produced -- leaving existing "
                  "graph_inferred_edges.json (if any) untouched")
            return 0
        with open(raw_path, "r", encoding="utf-8") as f:
            repo_extraction = json.load(f)

    # The skills registry is a separate sibling repo (spec §10: "vault *.md +
    # Brain *.py + skills registry") -- graphify only scans one target per
    # invocation, so it needs its own pass, merged with the repo pass below.
    skills_extraction = None
    if skills_file_map is not None:
        with tempfile.TemporaryDirectory(prefix="graph_enrich_skills_") as tmp:
            skills_raw_path = run_graphify_extract(args.skills, tmp, backend=args.backend)
            if skills_raw_path is not None:
                with open(skills_raw_path, "r", encoding="utf-8") as f:
                    skills_extraction = json.load(f)

    combined_extraction = merge_raw_extractions(repo_extraction, skills_extraction)
    edges = extract_inferred_edges(combined_extraction, canonical_graph, args.vault,
                                    args.repo_root, skills_file_map, args.min_confidence)

    write_inferred_edges(edges, args.out, args.min_confidence)
    print(f"graph_enrich: wrote {len(edges)} inferred edges -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
