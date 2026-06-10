#!/usr/bin/env python3
"""
graph_builder.py
THE HYPER BRAIN — Graph Memory Hub Phase 2+5

Refreshes the NOTES layer (Phase 2) and the SKILLS layer (Phase 5) of the
canonical memory-hub artifact (HYPERFOCUS_ZONE/06-AI-Context/graph.json).
The curated CODE layer (AST scan results, issues, statuses, ports) is
preserved untouched — only layer == "note"/"skill" nodes and generated
edge types (wikilink, mentions, skill-link) are rebuilt on each run.

Skills come from the HYPER-SILLs-By-WelshDog vault: skills-registry.json
provides the nodes, Graph-of-Skills frontmatter (depends_on/related)
provides skill↔skill edges, content scans provide skill→code and
note→skill mentions. If the skills repo is unreachable (container or
Actions runs), the existing skill layer is PRESERVED, never wiped.

Stdlib only — runs identically on the Windows host, inside the
agent-mcp-bridge container (vault at /vault), and in GitHub Actions.

Usage:
    python graph_builder.py                          # repo-relative defaults
    python graph_builder.py --vault /vault           # in-container
    python graph_builder.py --vault X --graph Y      # explicit paths
    python graph_builder.py --skills <HYPER-SILLs repo root>

BROski♾️
"""

import argparse
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_VAULT = os.path.join(REPO_ROOT, "HYPERFOCUS_ZONE")
DEFAULT_SKILLS = os.environ.get(
    "BRAIN_SKILLS_PATH",
    os.path.join(os.path.dirname(REPO_ROOT), "HYPER-SILLs-By-WelshDog"),
)
SKILL_ID_RE = re.compile(r"\bHS-\d{3}\b")

SKIP_DIRS = {".obsidian", "node_modules", "openhuman-build", "06-AI-Context"}
ATTACHMENT_RE = re.compile(
    r"\.(png|jpe?g|gif|svg|webp|pdf|mp4|mp3|wav|excalidraw|canvas)$", re.I
)
# [[Target]] / [[Target#heading]] / [[Target|alias]] / [[folder/Target]]
WIKILINK_RE = re.compile(r"\[\[([^\]\|#]+)(?:#[^\]\|]*)?(?:\|[^\]]*)?\]\]")


def scan_vault(vault_path):
    """Walk vault .md files.
    Returns (notes: basename -> relpath, links: [(src, dst)], contents: basename -> text)."""
    notes = {}
    links = []
    contents = {}
    for root, dirs, files in os.walk(vault_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fname in files:
            if not fname.endswith(".md"):
                continue
            fpath = os.path.join(root, fname)
            rel = os.path.relpath(fpath, vault_path).replace(os.sep, "/")
            base = fname[:-3]
            notes[base] = rel
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
            except OSError:
                continue
            contents[base] = content
            for m in WIKILINK_RE.finditer(content):
                target = m.group(1).strip().split("/")[-1]
                if not target or ATTACHMENT_RE.search(target):
                    continue
                links.append((base, target))
    return notes, links, contents


def code_id_patterns(graph):
    """Compiled name-matchers for curated code-layer ids.
    Matches both underscore and hyphen spellings (mcp_bridge / mcp-bridge)."""
    code_ids = [n["id"] for n in graph.get("nodes", [])
                if n.get("layer") not in ("note", "skill") and n["id"] != "scripts_dir"]
    patterns = {}
    for cid in code_ids:
        variants = {cid, cid.replace("_", "-")}
        patterns[cid] = re.compile(
            r"(?<![\w-])(" + "|".join(re.escape(v) for v in variants) + r")(?![\w-])",
            re.I,
        )
    return patterns


def build_mentions(graph, notes, contents):
    """Cross-layer edges (Phase 4): note text names a code module."""
    patterns = code_id_patterns(graph)
    edges = []
    for base in sorted(notes):
        content = contents.get(base, "")
        for cid, pat in patterns.items():
            if pat.search(content):
                edges.append({"from": f"note:{base}", "to": cid, "type": "mentions"})
    return edges


def parse_skill_frontmatter(content):
    """Pull depends_on / related HS-ids from a skill file's GoS frontmatter.
    Frontmatter sits AFTER the H1 line, so locate the first --- ... --- block."""
    m = re.search(r"^---\s*$(.*?)^---\s*$", content, re.M | re.S)
    if not m:
        return []
    refs = []
    current_key = None
    for line in m.group(1).splitlines():
        key_m = re.match(r"^(\w+):", line)
        if key_m:
            current_key = key_m.group(1)
            continue
        if current_key in ("depends_on", "related"):
            id_m = SKILL_ID_RE.search(line)
            if id_m and re.match(r"^\s*-", line):
                refs.append((current_key, id_m.group(0)))
    return refs


def scan_skills(skills_root):
    """Read skills-registry.json + skill files.
    Returns (skills: id -> registry entry, contents: id -> file text) or None
    if the skills repo isn't reachable (preserve-mode signal)."""
    registry_path = os.path.join(skills_root, "skills-registry.json")
    if not os.path.isfile(registry_path):
        return None
    with open(registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)
    skills = {}
    contents = {}
    for entry in registry.get("skills", []):
        sid = entry.get("id")
        if not sid:
            continue
        skills[sid] = entry
        fpath = os.path.join(skills_root, entry.get("file", "").replace("/", os.sep))
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                contents[sid] = f.read()
        except OSError:
            contents[sid] = ""
    return skills, contents


def build_skills_layer(graph, skills, skill_contents, note_contents):
    """Phase 5: HYPER-SILLs as graph layer 3.
    Nodes from the registry; skill↔skill edges from GoS frontmatter;
    skill→code mentions from content scan; note→skill mentions where a
    vault note names an HS-id. Unknown frontmatter HS-refs become phantom
    skill nodes (visible drift, same convention as phantom notes)."""
    edges = []
    degree = {}
    phantoms = set()
    seen = set()

    for sid in sorted(skills):
        for rel, target in parse_skill_frontmatter(skill_contents.get(sid, "")):
            if target == sid:
                continue
            key = (sid, target)
            if key in seen:
                continue
            seen.add(key)
            if target not in skills:
                phantoms.add(target)
            edges.append({"from": f"skill:{sid}", "to": f"skill:{target}",
                          "type": "skill-link", "rel": rel})
            degree[sid] = degree.get(sid, 0) + 1
            degree[target] = degree.get(target, 0) + 1

    patterns = code_id_patterns(graph)
    for sid in sorted(skills):
        content = skill_contents.get(sid, "")
        for cid, pat in patterns.items():
            if pat.search(content):
                edges.append({"from": f"skill:{sid}", "to": cid, "type": "mentions"})
                degree[sid] = degree.get(sid, 0) + 1

    for base in sorted(note_contents):
        for sid in set(SKILL_ID_RE.findall(note_contents[base])):
            if sid in skills:
                edges.append({"from": f"note:{base}", "to": f"skill:{sid}",
                              "type": "mentions"})
                degree[sid] = degree.get(sid, 0) + 1

    nodes = []
    for sid in sorted(skills):
        entry = skills[sid]
        nodes.append({
            "id": f"skill:{sid}",
            "layer": "skill",
            "title": entry.get("hero_name"),
            "emoji": entry.get("emoji"),
            "description": entry.get("description"),
            "category": entry.get("category"),
            "pack": entry.get("pack"),
            "path": entry.get("file"),
            "centrality": degree.get(sid, 0),
            "status": entry.get("status", "rescued"),
        })
    for sid in sorted(phantoms):
        nodes.append({
            "id": f"skill:{sid}",
            "layer": "skill",
            "path": None,
            "centrality": degree.get(sid, 0),
            "status": "phantom",
        })
    return nodes, edges


def build_notes_layer(notes, links):
    """Turn the vault scan into graph nodes + edges (note ids prefixed 'note:')."""
    degree = {}
    edges = []
    seen = set()
    phantoms = set()
    for src, dst in links:
        if src == dst:
            continue
        key = (src, dst)
        if key in seen:
            continue
        seen.add(key)
        if dst not in notes:
            phantoms.add(dst)
        edges.append({"from": f"note:{src}", "to": f"note:{dst}", "type": "wikilink"})
        degree[src] = degree.get(src, 0) + 1
        degree[dst] = degree.get(dst, 0) + 1

    nodes = []
    for base in sorted(notes):
        nodes.append({
            "id": f"note:{base}",
            "layer": "note",
            "path": notes[base],
            "centrality": degree.get(base, 0),
            "status": "live",
        })
    for base in sorted(phantoms):
        nodes.append({
            "id": f"note:{base}",
            "layer": "note",
            "path": None,
            "centrality": degree.get(base, 0),
            "status": "phantom",
        })
    return nodes, edges


def _touches_skill(edge):
    return (str(edge.get("from", "")).startswith("skill:")
            or str(edge.get("to", "")).startswith("skill:"))


def merge(graph, note_nodes, note_edges, mention_edges, notes_scanned,
          skill_nodes=None, skill_edges=None):
    """Replace the generated layers inside the existing graph, preserve the rest.
    skill_nodes/skill_edges None = skills repo unreachable this run — the
    previous skill layer is carried over untouched instead of being wiped."""
    kept_nodes = [n for n in graph.get("nodes", [])
                  if n.get("layer") not in ("note", "skill")]
    kept_edges = [e for e in graph.get("edges", [])
                  if e.get("type") not in ("wikilink", "mentions", "skill-link")]

    if skill_nodes is None:
        skill_nodes = [n for n in graph.get("nodes", []) if n.get("layer") == "skill"]
        skill_edges = [e for e in graph.get("edges", [])
                       if e.get("type") in ("mentions", "skill-link") and _touches_skill(e)]
        # carried-over note→skill mentions may point at notes that no longer exist
        note_ids = {n["id"] for n in note_nodes}
        skill_edges = [e for e in skill_edges
                       if not str(e["from"]).startswith("note:") or e["from"] in note_ids]

    graph["nodes"] = kept_nodes + note_nodes + skill_nodes
    graph["edges"] = kept_edges + note_edges + mention_edges + skill_edges

    meta = graph.setdefault("meta", {})
    meta["version"] = 4
    meta["layers"] = ["code", "notes", "mentions", "skills"]
    meta["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    meta["notes_scanned"] = notes_scanned
    meta["skills_indexed"] = sum(1 for n in skill_nodes if n.get("status") != "phantom")
    meta["total_nodes"] = len(graph["nodes"])
    meta["total_edges"] = len(graph["edges"])
    return graph


def main():
    parser = argparse.ArgumentParser(
        description="Rebuild the notes + skills layers of graph.json")
    parser.add_argument("--vault", default=DEFAULT_VAULT, help="Vault root path")
    parser.add_argument("--graph", default=None,
                        help="graph.json path (default: <vault>/06-AI-Context/graph.json)")
    parser.add_argument("--skills", default=DEFAULT_SKILLS,
                        help="HYPER-SILLs repo root (env BRAIN_SKILLS_PATH; "
                             "missing = preserve existing skill layer)")
    args = parser.parse_args()

    graph_path = args.graph or os.path.join(args.vault, "06-AI-Context", "graph.json")
    if not os.path.isdir(args.vault):
        sys.exit(f"vault not found: {args.vault}")
    if not os.path.isfile(graph_path):
        sys.exit(f"graph.json not found: {graph_path}")

    with open(graph_path, "r", encoding="utf-8") as f:
        graph = json.load(f)

    notes, links, contents = scan_vault(args.vault)
    note_nodes, note_edges = build_notes_layer(notes, links)
    mention_edges = build_mentions(graph, notes, contents)

    skill_nodes = skill_edges = None
    scanned = scan_skills(args.skills)
    if scanned is None:
        print(f"skills repo not reachable at {args.skills} — "
              "preserving existing skill layer")
    else:
        skills, skill_contents = scanned
        skill_nodes, skill_edges = build_skills_layer(
            graph, skills, skill_contents, contents)

    graph = merge(graph, note_nodes, note_edges, mention_edges, len(notes),
                  skill_nodes, skill_edges)

    # atomic write so a half-written file is never served by /graph
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(graph_path), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        json.dump(graph, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, graph_path)

    skill_count = len([n for n in graph["nodes"] if n.get("layer") == "skill"])
    print(f"graph.json v{graph['meta']['version']} — "
          f"{graph['meta']['total_nodes']} nodes / {graph['meta']['total_edges']} edges "
          f"({len(note_nodes)} note nodes, {len(note_edges)} wikilink edges, "
          f"{len(mention_edges)} mentions edges, {skill_count} skill nodes, "
          f"{len(notes)} notes scanned)")


if __name__ == "__main__":
    main()
