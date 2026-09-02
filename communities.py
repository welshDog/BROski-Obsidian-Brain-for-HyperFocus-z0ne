#!/usr/bin/env python3
"""
communities.py
THE HYPER BRAIN — Graph Memory Hub v5

Pure stdlib graph math for the canonical memory-hub artifact
(HYPERFOCUS_ZONE/06-AI-Context/graph.json):

  pagerank()          -> centrality_global per node
  detect_communities() -> deterministic greedy-modularity partition
  derive_labels()     -> provisional community labels, no LLM

Runs identically on the Windows host, inside the agent-mcp-bridge container,
and in GitHub Actions. Deterministic: identical input -> identical output,
independent of dict/set iteration order.

BROski♾️
"""

# Retrieval topology: the only edge types RAG expansion follows.
FILTERED_EDGE_TYPES = ("wikilink", "mentions", "skill-link")


def _adjacency(nodes, edges):
    """Undirected adjacency over FILTERED_EDGE_TYPES only.
    Every node id is a key; isolated nodes map to an empty set. Self-loops and
    endpoints not present in `nodes` are dropped."""
    ids = {n["id"] for n in nodes}
    adj = {nid: set() for nid in ids}
    for e in edges:
        if e.get("type") not in FILTERED_EDGE_TYPES:
            continue
        a, b = e.get("from"), e.get("to")
        if a in ids and b in ids and a != b:
            adj[a].add(b)
            adj[b].add(a)
    return adj


def _mode(seq):
    """Most common value in `seq`; ties broken by sorted value. Deterministic.
    Returns (value, count) or (None, 0) for an empty sequence."""
    counts = {}
    for x in seq:
        counts[x] = counts.get(x, 0) + 1
    best_x, best_c = None, 0
    for x in sorted(counts):
        if counts[x] > best_c:
            best_x, best_c = x, counts[x]
    return best_x, best_c


def pagerank(nodes, edges, damping=0.85, tol=1.0e-6, max_iter=100):
    """Deterministic undirected PageRank over the filtered adjacency.

    Returns {node_id: score}. Dangling (edge-isolated) nodes converge to one
    shared floor value. Iteration over neighbours is sorted so float addition
    order — and therefore the 6-dp-rounded result — is stable run to run.
    """
    adj = _adjacency(nodes, edges)
    ids = sorted(adj)
    n = len(ids)
    if n == 0:
        return {}
    rank = {nid: 1.0 / n for nid in ids}
    deg = {nid: len(adj[nid]) for nid in ids}
    for _ in range(max_iter):
        dangling = damping * sum(rank[nid] for nid in ids if deg[nid] == 0) / n
        base = (1.0 - damping) / n + dangling
        new = {nid: base for nid in ids}
        for nid in ids:
            d = deg[nid]
            if d == 0:
                continue
            share = damping * rank[nid] / d
            for nb in sorted(adj[nid]):
                new[nb] += share
        delta = sum(abs(new[nid] - rank[nid]) for nid in ids)
        rank = new
        if delta < tol:
            break
    return rank
