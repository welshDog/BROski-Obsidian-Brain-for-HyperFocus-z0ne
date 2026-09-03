# Constellation — Community Coloring

> **Status:** design — awaiting review
> **Date:** 2026-09-03
> **Branch:** `constellation-community-coloring`
> **Author:** Lyndz + Claude (brainstorming session)
> **Follows:** `2026-09-02-graph-brain-v5-communities-design.md` (§10-adjacent — the "richer constellation viz" increment that spec explicitly deferred)

---

## 1. Problem

Graph Brain v5 stamped `community`, `community_label`, and `centrality_global`
onto every node of `HYPERFOCUS_ZONE/06-AI-Context/graph.json`. The D3 force-graph
served at `:3302/constellation` (`.agents/mcp-bridge/constellation.html`) reads
`/graph`, renders it, and its header now correctly shows *graph v5* — but the
viz **ignores the community fields entirely**. Nodes are colored by `layer`
(note / skill / code / dead), so the 11 real communities the v5 partition found
are invisible on the map.

## 2. Goal

Let the constellation **color and focus by community**, so the vault's real
topical clusters are visible and explorable, without losing the existing
layer-colored view.

### Non-goals

- No change to `/graph`, `/graph/related`, `graph_builder.py`, `communities.py`,
  or `mcp_bridge.py`. This is one static HTML file.
- No change to node sizing (stays `centrality`-based), edge rendering, the force
  simulation, search, or the side-panel `/graph/related` lookups.
- No new dependency — D3 v7 is already loaded from the CDN.
- Not a general theming system; two color modes, nothing configurable.

## 3. Approach

One design, below. The only alternative considered — a **static color key**
(legend as a non-interactive swatch list) — was rejected: matching ~11 colors
by eye against the map is friction, and it hides the 105 edge-isolated singleton
notes in the muted tail instead of making them a thing you can click. The
chosen design makes community focus a one-click, zero-reading action.

## 4. Design

### 4.1 Color-mode toggle

A new chip in `.controls` (top-right), above the legend:

```
◑  colour · community        ◑  colour · layer
```

- Two modes: `community` (default) and `layer` (today's behaviour).
- Clicking the chip toggles the mode. On toggle:
  - node fills transition (200ms) between `communityColor(d)` and `COLORS[d.g]`;
  - the side-panel badge color follows the active mode;
  - the legend is rebuilt for the new mode (§4.3);
  - any active focus/filter state from the previous mode is cleared (all nodes
    return to full opacity / visible).
- `community` is the default so the v5 clustering is what you see on load.

### 4.2 Community palette + assignment

```
PALETTE = [
  "#22d3ee",  // cyan   — page brand
  "#a78bfa",  // violet — page brand
  "#f59e0b",  // gold   — page brand
  "#34d399",  // emerald
  "#f472b6",  // pink
  "#60a5fa",  // blue
  "#fb7185",  // rose
  "#a3e635",  // lime
  "#c084fc",  // light purple
  "#fbbf24",  // amber
  "#2dd4bf",  // teal
]
MUTED = "#4b5563"   // slate — singletons and the long tail
```

Assignment, computed once after `/graph` loads:

1. Group nodes by `community`; count members per community.
2. Keep communities with **≥ 2 members** ("real" communities); sort them by
   member count desc, ties broken by community id asc (deterministic).
3. `communityColorMap[community_id] = PALETTE[i]` for the first
   `PALETTE.length` real communities; every other community (singletons, and
   any real community past index 10) → `MUTED`.
4. `communityColor(node)` returns `communityColorMap[node.community] ?? MUTED`.

On the live v5 graph this colors the 11 multi-node communities (sizes
46 / 38 / 29 / 11 / 9 / 8 / 7 / 5 / 4 / 3 / 3) and mutes the 105 singletons —
the palette has one spare slot.

### 4.3 Legend (mode-dependent)

The legend container is rebuilt on every mode change.

**Layer mode** — unchanged from today: four chips (`notes` / `skills` / `code` /
`dead`), each a **visibility toggle** (`display: none` on hide), showing the
layer color dot + count.

**Community mode** — one chip per real community, plus one tail chip:

- Chip content: color dot · `community_label` · member count.
- Chips wrap (the container becomes `flex-wrap: wrap`, right-aligned).
- Order: same size-desc order as the palette assignment.
- One trailing chip `· isolated · <N>` in `MUTED` for all singleton/tail nodes.
- **Community chips are focus toggles, not hide toggles.** Clicking a chip adds
  its community to a *focused set*; nodes **not** in any focused community dim
  to `fill-opacity: 0.12` (reusing the exact opacity the existing hover
  `focus()` already uses), their labels dim to `0.15`, and edges between two
  dimmed nodes drop to `0.15`. Clicking a lit chip removes it from the set.
  Empty focused set → everything at full opacity. Multiple chips = union.
- This is the "click a community → it stays lit, everything else dims" behaviour
  — instant focus, no legend-scanning. Clicking empty SVG space (which already
  calls `unfocus()` + `closePanel()`) also clears the focused set.

The hide-vs-focus split between the two modes' legends is deliberate: layer is a
coarse "show me only X"; community is "pull this cluster forward". Each legend
does the thing that mode is for.

The community focused-set is the new **resting state** while it is non-empty:
node hover-focus still works on top of it (transient dim-to-neighbours), and
`unfocus()` must return to the community-focused opacities, not to full
opacity — so the existing `focus()`/`unfocus()` need to read the focused-set,
not just `pinned`.

### 4.4 Tooltip + side panel

- **Tooltip** (`node.on("mouseover")`): append the community when known —
  `<id> · <layer> · <community_label>`. When the node is in the muted tail,
  show `· isolated` instead of a label.
- **Panel meta** (`openPanel`): add a line
  `community <b><community_label></b> · <b><N></b> nodes` (omitted when the node
  has no `community` field, i.e. a v4 graph).

### 4.5 What is untouched

`radius()` (still `centrality`), `edgeColor()`, the force simulation, `focus()` /
`unfocus()` internals, search, drag, zoom, `/graph/related` panel lookups, the
header stats line, and the entrance reveal. `COLORS` and `group()` stay for
layer mode. On a **v4 graph** (no `community` fields) the toggle still works but
`communityColor` returns `MUTED` for everything and the community legend shows a
single `isolated` chip — degrades to a flat map, never breaks.

## 5. Data facts (live v5 graph, 2026-09-02)

| Fact | Value |
|---|---|
| Total nodes / edges | 268 / 482 |
| `communities_count` | 116 |
| Real (≥2-member) communities | 11 — sizes 46, 38, 29, 11, 9, 8, 7, 5, 4, 3, 3 |
| Singletons | 105 (edge-isolated notes) |
| `community_label` examples | PARA path segments (`00-Inbox`, `03-Resources`), `<id> cluster` fallbacks |
| `community` id shape | smallest member node-id, e.g. `hyper_brain_core`, `note:Dashboard` |

Note: `community_label` quality is a known v5 follow-up (it currently picks the
first PARA path segment). The legend shows whatever label the graph carries;
improving the labels is out of scope here.

## 6. Testing

There is no JS test harness for `constellation.html` today (`test_constellation.py`
covers `constellation_builder.py`, a different file — it must stay green,
untouched).

**New: `tests/test_constellation_page.py`** — static, stdlib + pytest only:

- The file parses as a single well-formed HTML document (one `<script>` block,
  balanced tags via `html.parser`).
- The inline script passes `node --check` when extracted to a temp `.js` file
  (classic script, not ESM — `node --check` is valid here; skip the test with a
  clear reason if `node` is not on PATH).
- Required identifiers are present: `PALETTE`, `MUTED`, `communityColor`,
  `communityColorMap`, `fillFor` (or the chosen fill dispatch name), the mode
  toggle element id, and `community_label`.
- `PALETTE` literal has ≥ 10 entries and `MUTED` is a distinct hex not in
  `PALETTE`.
- Regression guard: `COLORS`, `group`, `radius`, `edgeColor`, the search
  handler, and the `/graph/related` fetch are all still referenced (nothing
  from §4.5 was removed).

**Manual verification checklist** (in the implementation plan, run once on the
deployed page — a viz's real test is the eye):

1. Page loads in **community** mode; the 11 clusters are distinctly colored,
   the bulk of the map is muted slate.
2. Toggle to **layer** → the old note/skill/code coloring returns; the 4-chip
   layer legend is back and its hide toggles still work.
3. Toggle back to **community** → click the largest community chip → that
   cluster stays lit, everything else dims; click a second chip → both lit;
   click a lit chip → it dims again; click empty space → all restored.
4. Click the `isolated` chip → the 105 singletons light, the clusters dim.
5. Hover a clustered node → tooltip shows the `community_label`; click it →
   panel shows the `community … · N nodes` line.
6. `curl -s :3302/graph` still `version 5`; `/route` unaffected.

## 7. Deployment

`constellation.html` is served by `agent-mcp-bridge` via `FileResponse` from
`/app/constellation.html` (re-read per request). Deploy:

```
docker cp .agents/mcp-bridge/constellation.html agent-mcp-bridge:/app/constellation.html
```

Live immediately — **no restart**. Fold into the next proper image rebuild
(`HyperCode-V2.4/` four-file compose + `--profile brain-agents`, per
`NEXT_SESSION_HANDOVER_2026-09-02.md`). The page is also linked from the Brain
`/ui` nav tab and the IDE TopBar — both just point a browser at
`:3302/constellation`, so no change there.

## 8. Files touched

| File | Change | ~LOC |
|---|---|---|
| `.agents/mcp-bridge/constellation.html` | mode toggle, `PALETTE`/`MUTED`, `communityColor` + assignment, fill dispatch, mode-dependent legend rebuild with community focus-toggles, tooltip + panel additions | ~90 changed / added |
| `tests/test_constellation_page.py` | **new** — static structure + identifier + `node --check` gate | ~70 |
| `NEXT_SESSION_HANDOVER_2026-09-03.md` or the v5 followups doc | note the constellation increment shipped | ~4 |

Implementation on branch `constellation-community-coloring`, single commit or a
2-commit split (viz / test), deployed by `docker cp`, merged after the manual
checklist passes.

## 9. Open questions for implementation

1. **Palette hues** — the set in §4.2 is chosen for legibility on `#050505` and
   distinctness; a design-brain pass at implementation time may nudge 2-3 hues
   for better mutual separation (e.g. `#f472b6` vs `#fb7185` vs `#c084fc` are
   close). The count and the "brand-three-first, muted tail" structure are
   fixed; the exact hexes are tunable.
2. **`community_label` collisions** — several communities may carry the same
   PARA-segment label (`00-Inbox`) until the v5 label follow-up lands. The
   legend should disambiguate with the member count already shown, and fall
   back to the community id in the chip `title` attribute.
3. **Chip overflow** — 11 + 1 chips right-aligned and wrapping may crowd the
   search box on a narrow window. If it does, cap visible chips at 8 with a
   `+N` expander; decide against the real rendered page.
