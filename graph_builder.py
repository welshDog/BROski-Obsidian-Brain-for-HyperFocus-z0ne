#!/usr/bin/env python3
"""
graph_builder.py
THE HYPER BRAIN — Graph Memory Hub Phase 2

Refreshes the NOTES layer of the canonical memory-hub artifact
(HYPERFOCUS_ZONE/06-AI-Context/graph.json) by scanning the vault for
Obsidian wiki-links. The curated CODE layer (AST scan results, issues,
statuses, ports) is preserved untouched — only layer == "note" nodes and
type == "wikilink" edges are rebuilt on each run.

Stdlib only — runs identically on the Windows host, inside the
agent-mcp-bridge container (vault at /vault), and in GitHub Actions.

Usage:
    python graph_builder.py                          # repo-relative defaults
    python graph_builder.py --vault /vault           # in-container
    python graph_builder.py --vault X --graph Y      # explicit paths

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


def build_mentions(graph, notes, contents):
    """Cross-layer edges (Phase 4): note text names a code module.
    Matches both underscore and hyphen spellings (mcp_bridge / mcp-bridge)."""
    code_ids = [n["id"] for n in graph.get("nodes", [])
                if n.get("layer") != "note" and n["id"] != "scripts_dir"]
    patterns = {}
    for cid in code_ids:
        variants = {cid, cid.replace("_", "-")}
        patterns[cid] = re.compile(
            r"(?<![\w-])(" + "|".join(re.escape(v) for v in variants) + r")(?![\w-])",
            re.I,
        )
    edges = []
    for base in sorted(notes):
        content = contents.get(base, "")
        for cid in code_ids:
            if patterns[cid].search(content):
                edges.append({"from": f"note:{base}", "to": cid, "type": "mentions"})
    return edges


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


def merge(graph, note_nodes, note_edges, mention_edges, notes_scanned):
    """Replace the generated layers inside the existing graph, preserve the rest."""
    kept_nodes = [n for n in graph.get("nodes", []) if n.get("layer") != "note"]
    kept_edges = [e for e in graph.get("edges", [])
                  if e.get("type") not in ("wikilink", "mentions")]
    graph["nodes"] = kept_nodes + note_nodes
    graph["edges"] = kept_edges + note_edges + mention_edges

    meta = graph.setdefault("meta", {})
    meta["version"] = 3
    meta["layers"] = ["code", "notes", "mentions"]
    meta["updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    meta["notes_scanned"] = notes_scanned
    meta["total_nodes"] = len(graph["nodes"])
    meta["total_edges"] = len(graph["edges"])
    return graph


def main():
    parser = argparse.ArgumentParser(description="Rebuild the notes layer of graph.json")
    parser.add_argument("--vault", default=DEFAULT_VAULT, help="Vault root path")
    parser.add_argument("--graph", default=None,
                        help="graph.json path (default: <vault>/06-AI-Context/graph.json)")
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
    graph = merge(graph, note_nodes, note_edges, mention_edges, len(notes))

    # atomic write so a half-written file is never served by /graph
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(graph_path), suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        json.dump(graph, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, graph_path)

    print(f"graph.json v{graph['meta']['version']} — "
          f"{graph['meta']['total_nodes']} nodes / {graph['meta']['total_edges']} edges "
          f"({len(note_nodes)} note nodes, {len(note_edges)} wikilink edges, "
          f"{len(mention_edges)} mentions edges, {len(notes)} notes scanned)")


if __name__ == "__main__":
    main()
