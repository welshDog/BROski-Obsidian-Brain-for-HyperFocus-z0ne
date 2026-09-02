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


def detect_communities(nodes, edges, gamma=1.0):
    """Deterministic greedy-modularity (Clauset-Newman-Moore) agglomeration
    over the filtered adjacency.

    Returns (node_community, members):
      node_community[node_id] -> community id (== smallest member node-id)
      members[community_id]    -> sorted list of member node-ids

    No randomness; selection is an argmax over a total order, so dict/set
    iteration order cannot change the result.
    """
    adj = _adjacency(nodes, edges)
    ids = sorted(adj)

    edge_pairs = set()
    for nid in ids:
        for nb in adj[nid]:
            edge_pairs.add((nid, nb) if nid < nb else (nb, nid))
    m = len(edge_pairs)

    node_comm = {nid: nid for nid in ids}
    members = {nid: [nid] for nid in ids}
    if m == 0:
        return node_comm, members

    deg = {nid: len(adj[nid]) for nid in ids}
    a = {nid: float(deg[nid]) for nid in ids}      # sum of degrees per community
    two_m = 2.0 * m

    # cut map: edges between distinct communities, keyed (c_lo, c_hi)
    e_between = {}
    for u, v in sorted(edge_pairs):
        c1, c2 = node_comm[u], node_comm[v]
        key = (c1, c2) if c1 < c2 else (c2, c1)
        e_between[key] = e_between.get(key, 0.0) + 1.0

    for _ in range(len(ids)):                       # hard cap = node count
        best = None                                # (dQ, key, c_keep, c_drop)
        for (c1, c2), e_uv in e_between.items():
            if e_uv <= 0.0:
                continue
            dQ = 2.0 * (e_uv / two_m
                        - gamma * (a[c1] * a[c2]) / (two_m * two_m))
            if dQ <= 0.0:
                continue
            if best is None or dQ > best[0] or (dQ == best[0] and (c1, c2) < best[1]):
                best = (dQ, (c1, c2), c1, c2)
        if best is None:
            break
        _, _, ca, cb = best
        keep, drop = (ca, cb) if ca < cb else (cb, ca)

        members[keep].extend(members[drop])
        members[keep].sort()
        for nid in members[drop]:
            node_comm[nid] = keep
        del members[drop]
        a[keep] += a[drop]
        del a[drop]

        merged = {}
        for (x, y), w in e_between.items():
            nx = keep if x in (ca, cb) else x
            ny = keep if y in (ca, cb) else y
            if nx == ny:
                continue                           # now intra-community
            k = (nx, ny) if nx < ny else (ny, nx)
            merged[k] = merged.get(k, 0.0) + w
        e_between = merged

    return node_comm, members


def derive_labels(members, nodes, pagerank):
    """Provisional community labels, no LLM. Deterministic.

    1. common first path-segment among note: members (>= 60%)
    2. '<dominant skill category> skills'
    3. '<highest centrality_global member id> cluster'
    """
    by_id = {n["id"]: n for n in nodes}
    labels = {}
    for cid in sorted(members):
        mem = members[cid]

        segs = [by_id[nid]["path"].split("/")[0]
                for nid in mem
                if by_id.get(nid, {}).get("layer") == "note"
                and by_id[nid].get("path")]
        if segs:
            top_seg, count = _mode(segs)
            if count / len(segs) >= 0.6:
                labels[cid] = top_seg
                continue

        cats = [by_id[nid]["category"]
                for nid in mem
                if by_id.get(nid, {}).get("layer") == "skill"
                and by_id[nid].get("category")]
        if cats:
            labels[cid] = f"{_mode(cats)[0]} skills"
            continue

        top = max(sorted(mem), key=lambda nid: pagerank.get(nid, 0.0))
        labels[cid] = f"{top} cluster"
    return labels
