# Graph Brain v5 — deferred follow-ups

From the SDD run of `2026-09-02-graph-brain-v5-communities.md`. None of these blocked the merge; the whole-branch final review verdict was "ready to merge with fixes" and the one merge-blocker (fail-open field hygiene) was fixed in commit `24337ec`. These are the residual minor findings.

## 1. `derive_labels` picks the wrong path segment
`communities.py` `derive_labels()` uses `path.split("/")[0]` — the **first** PARA segment — so community labels come out as `"00-Inbox"`, `"03-Resources"`, `"99-Templates"` (near-useless: almost every note lives in one of ~8 top folders), and vault-root notes with no `/` get the raw filename including extension.

Spec §5.4's worked example implies the **last meaningful** segment (`note:02-Areas/Focus-Analytics/*` → `"Focus-Analytics"`). `tests/test_communities.py` (the `test_derive_labels_common_path_segment` test) asserts `"02-Areas"`, encoding the deviation — it must be updated together with the fix.

Impact: cosmetic. Labels are `community_label` only; the `community` id (smallest member node-id) is what drives all scoring.

## 2. `related_by_community` over-excludes (spec §6.4 deviation)
`mcp_bridge.py` `/graph/related` builds its exclusion set from the **full** `related` pool (`related_nodes(..., limit=max(limit*3, 15))`), not the three `[:limit]` slices actually returned. Spec §6.4 says exclude only what's "already in `related_paths`/`related_code`/`related_skills`".

Measured: `related_by_community` is `[]` for 137/268 nodes as built vs 119/268 under spec semantics — 18 nodes (7%) lose a transparency list they should show. The plan's Task 5 Step 4 code was the source of the wider exclusion.

Impact: never wrong data, just an emptier transparency field on 7% of nodes.

## 3. Endpoint wiring guard is substring-only
`tests/test_bridge_community_scoring.py` — the `test_graph_related_endpoint_wires_related_by_community` guard asserts the substrings `community_members(` and `"related_by_community"` both appear in the module source, but not that they're bound as key→value. Tighten to a single regex, e.g. `"related_by_community":\s*by_community`.

## 4. Record the spec §11 open-question answers
`docs/superpowers/specs/2026-09-02-graph-brain-v5-communities-design.md` §11 still reads as open questions. Fill in from the Task 3 calibration:
- **§11.1 (gamma):** `gamma = 1.0` kept. Real partition = 116 communities over 268 nodes, but 105 are edge-isolated singletons (degree 0 in the filtered topology — gamma cannot merge them). The connected partition is **11 communities over 163 nodes, largest 28.2%** — inside the target band. Not degenerate.
- **§11.2 (PageRank range):** observed `centrality_global` on the real graph: min `0.000839`, max `0.022876`, mean `0.003731` (max/avg ≈ 6.13). The `pr * n_count` normalisation in `_cent()` lands an average node near 1.0 as designed.
- **§11.3 (fixture cases):** `tests/fixtures/retrieval_cases.json` — 13 cases, 2 tagged `gap`. See follow-up 6.

## 5. Sort `graph["edges"]` before write (pre-existing, not introduced here)
`graph_builder.py` builds the edges list from `set` iteration, so `graph.json`'s `edges` array has run-to-run serialization-order churn (the v5 regen diff showed `mentions` edges re-sequenced within some `from` nodes, even though the edge multiset is identical). This predates Graph Brain v5. Add `graph["edges"].sort(key=lambda e: (e["from"], e["to"], e["type"]))` (or similar) before the atomic write to make the committed file byte-stable and kill diff noise on every CI regen.

## 6. Retrieval-regression gate: recall dimension is thin on the current vault
`tests/test_retrieval_regression.py` — only **2** genuine "edge-less same-community" gap cases exist on the vault as it stands, and both seed on `difficulty_dial`. This is structural: 63 note-layer nodes are edge-isolated (→ singleton communities → community-seeded expansion can never reach them), and every other multi-node community is dense enough via the Brain-Constellation hub notes that v4's 2-hop ranker already reaches the targets. 9 of the 13 gate cases are skill-anchored and inert at v4 = v5 = 1.0.

The gate's **no-regression** half is non-vacuous (2 note-axis cases at v4 0.5 / v5 1.0 would catch a regression). v5's measurable benefit on this vault is **ranking quality**, plus a net **+10 / −1** change in notes that gain a linked RAG context file.

Action: re-check the gap-case count when vault link density rises (more wikilinks between currently-isolated notes). Consider a `gamma` retune only if isolated-note linking increases enough to create real multi-node communities among them. Not a defect.

## 7. `meta.communities_count` is misleading
It reports `116`, which reads as a degenerate partition. Consider splitting it in `meta` into connected vs isolated (`communities_count: 11`, `isolated_nodes: 105`) so a reader isn't alarmed.
