# Constellation Community Coloring — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Colour the `:3302/constellation` force-graph by Graph Brain v5 community, with a `community ⇄ layer` mode toggle and a click-to-focus community legend, in one static HTML file.

**Architecture:** All changes are in `.agents/mcp-bridge/constellation.html`'s single inline `<script>`. A `colorMode` variable drives a `fillFor(node)` dispatch between the existing `COLORS[layer]` map and a new `communityColor(node)` built from a size-ranked palette. The legend is rebuilt per mode: layer mode keeps today's hide-toggle chips; community mode gets focus-toggle chips that dim everything outside a `focusedComms` set, reusing the existing `focus()` opacity values. No API, Python, or dependency change.

**Tech Stack:** Vanilla ES2017 (one IIFE), D3 v7 (already loaded from cdnjs in the page). Tests: `pytest` + `node --check` for a JS syntax gate.

**Spec:** `docs/superpowers/specs/2026-09-03-constellation-community-coloring-design.md` — read it alongside this plan.

## Global Constraints

- **One file for the viz:** `.agents/mcp-bridge/constellation.html`. Do NOT touch `/graph`, `/graph/related`, `graph_builder.py`, `communities.py`, `mcp_bridge.py`, or any other served file.
- **No new dependency.** D3 v7 is already `<script src=…d3@7…>`. No new `<script>` tags, no npm.
- **Default `colorMode = "community"`** so the v5 clustering is what loads.
- **On every mode toggle:** clear the *other* mode's interaction state — reset `focusedComms` to empty AND reset layer `visible` to all-true — then rebuild the legend.
- **Community chips are focus toggles:** a node outside every focused community goes to `fill-opacity: 0.12`, its label to `opacity: 0.15`, and an edge with both endpoints dimmed to `stroke-opacity: 0.15`. These are the exact values the existing `focus()` already uses — reuse them, don't invent new ones.
- **Layer chips stay hide toggles** (`display: none`), behaviour unchanged from today.
- **v4-graph safe:** with no `community` field on nodes, `communityColor` returns `MUTED` for all, the community legend shows a single `isolated` chip, and nothing throws.
- **`PALETTE`** has ≥ 10 hex entries, the page's brand three (`#22d3ee`, `#a78bfa`, `#f59e0b`) first; **`MUTED`** is a distinct hex not in `PALETTE`. Community→colour assignment is deterministic: real (≥2-member) communities sorted by member count desc, ties broken by community id ascending.
- **`tests/test_constellation.py` is not touched and must stay green** (it covers `constellation_builder.py`, a different file).
- **Deploy** (after merge): `docker cp .agents/mcp-bridge/constellation.html agent-mcp-bridge:/app/constellation.html` — served by `FileResponse`, re-read per request, **no restart**. Fold into the next image rebuild.
- **Commits:** conventional-commit subjects; end every commit body with
  `Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>` and
  `Claude-Session: https://claude.ai/code/session_012RjkCXg6AFBdQaUbtoW6Nf`.
- **Branch:** `constellation-community-coloring` (already created off `main`; the spec commit `5991feb` is on it). A local watcher regenerates `HYPERFOCUS_ZONE/06-AI-Context/graph.json` / `embeddings.json` out of band — never stage those; `git checkout` them if dirty before committing.

---

## File Structure

| File | New/Mod | Responsibility |
|---|---|---|
| `.agents/mcp-bridge/constellation.html` | modify (inline `<script>` only) | `colorMode` + `fillFor()`; `PALETTE`/`MUTED`/`communityColor()` + size-ranked assignment; mode-toggle chip; `renderLegend()` (layer branch = today's chips; community branch = focus-toggle chips + `isolated` chip); `focusedComms` set + `applyCommunityFocus()`; `focus()`/`unfocus()` made focus-set-aware; tooltip + panel `community_label` lines; panel badge uses `fillFor` |
| `tests/test_constellation_page.py` | **new** | static structure lock: single well-formed HTML doc; inline script passes `node --check`; required identifiers present; `PALETTE` ≥ 10 + distinct `MUTED`; regression guard that nothing from spec §4.5 was removed |
| `NEXT_SESSION_HANDOVER_2026-09-03.md` | **new** (or append if it exists) | one 🟢 line: constellation community coloring shipped + the `docker cp` deploy line |

---

## Task 1: Colouring core + mode toggle

**Files:**
- Modify: `.agents/mcp-bridge/constellation.html` (inline `<script>`, and one chip in the `.controls` markup)

**Interfaces:**
- Consumes: `graph.nodes[].community` / `.community_label` (v5 fields, may be absent), the existing `COLORS`, `group()`, `node`/`label` D3 selections, `openPanel()`.
- Produces (Task 2 relies on these names): `colorMode` (`"community"|"layer"` let-binding), `fillFor(d) -> hex`, `PALETTE` (array), `MUTED` (hex), `communityColor(d) -> hex`, `communityColorMap` (`Map<id,hex>`), `commSize` (`Map<id,count>`), `realComms` (`Array<[id,count]>` size-desc), `setMode(next)` function, and an element `#modeToggle`.

- [ ] **Step 1: Add the mode-toggle chip to the controls markup**

In the `.controls` block (currently the search input + `<div class="legend" id="legend">`), insert a chip **above** the legend:

```html
<div class="controls">
  <input class="search" id="search" type="search" placeholder="find a star…"
         autocomplete="off" spellcheck="false">
  <div class="chip" id="modeToggle" role="button" tabindex="0" aria-pressed="true"
       title="Toggle node colour: community clusters vs code layer">
    <span class="dot" id="modeDot"></span><span id="modeLabel">colour · community</span>
  </div>
  <div class="legend" id="legend"></div>
</div>
```

(`.chip` and `.chip .dot` styles already exist. `#modeDot` gets its colour set from JS.)

- [ ] **Step 2: Add `colorMode`, palette, and `communityColor` — after the `nodes`/`links` build**

Immediately after `const links = graph.edges … .map(…)` (currently ~line 158), before the `counts` block:

```js
  // ── community colouring (v5) ───────────
  let colorMode = "community";                 // "community" | "layer"

  const PALETTE = ["#22d3ee","#a78bfa","#f59e0b","#34d399","#f472b6",
                   "#60a5fa","#fb7185","#a3e635","#c084fc","#fbbf24","#2dd4bf"];
  const MUTED = "#4b5563";

  const commSize = new Map();
  nodes.forEach(n => {
    if (n.community) commSize.set(n.community, (commSize.get(n.community) || 0) + 1);
  });
  const realComms = [...commSize.entries()]
    .filter(([, c]) => c >= 2)
    .sort((a, b) => b[1] - a[1] || (a[0] < b[0] ? -1 : 1));   // size desc, id asc
  const communityColorMap = new Map();
  realComms.forEach(([id], i) => { if (i < PALETTE.length) communityColorMap.set(id, PALETTE[i]); });

  const communityColor = d => communityColorMap.get(d.community) ?? MUTED;
  const fillFor = d => colorMode === "community" ? communityColor(d) : COLORS[d.g];
```

- [ ] **Step 3: Use `fillFor` for the initial node fill and the panel badge**

Change the node `.attr("fill", d => COLORS[d.g])` (currently ~line 191) to:

```js
    .attr("fill", d => fillFor(d))
```

In `openPanel(d)` change the badge colour lines (currently ~line 285):

```js
    badge.style.color = fillFor(d); badge.style.borderColor = fillFor(d);
```

- [ ] **Step 4: Add `setMode()` and wire the toggle**

After the legend code is set up is fine, but the function only needs `node`, `renderLegend` (Task 2), `focusedComms` (Task 2), `visible` (existing). Add near the other control wiring (after the `svg.on("click", …)` handler, ~line 258). For Task 1, `renderLegend`/`focusedComms` don't exist yet — guard so Task 1 is independently runnable and Task 2 fills them in:

```js
  // ── colour mode toggle ─────────────────
  const modeToggle = document.getElementById("modeToggle");
  const modeDot = document.getElementById("modeDot");
  const modeLabel = document.getElementById("modeLabel");

  function setMode(next) {
    colorMode = next;
    modeLabel.textContent = `colour · ${next}`;
    modeToggle.setAttribute("aria-pressed", String(next === "community"));
    modeDot.style.background = next === "community" ? PALETTE[0] : COLORS.code;
    node.transition().duration(200).attr("fill", d => fillFor(d));
    if (pinned) {                               // keep an open panel's badge in sync
      const b = document.getElementById("panelBadge");
      b.style.color = fillFor(pinned); b.style.borderColor = fillFor(pinned);
    }
    if (typeof focusedComms !== "undefined") focusedComms.clear();
    Object.keys(visible).forEach(k => visible[k] = true);
    node.attr("display", null); label.attr("display", null); link.attr("display", null);
    if (typeof renderLegend === "function") renderLegend();
    unfocus();
  }
  modeToggle.addEventListener("click", () => setMode(colorMode === "community" ? "layer" : "community"));
  modeToggle.addEventListener("keydown", e => {
    if (e.key === "Enter" || e.key === " ") { e.preventDefault(); modeToggle.click(); }
  });
  modeDot.style.background = PALETTE[0];        // initial: community mode
```

- [ ] **Step 5: Syntax-gate the script**

Run:
```bash
cd "H:/HYPERFOCUSZONE/HperCore/BROski-Obsidian-Brain-for-HyperFocus-z0ne"
python -c "import re; h=open('.agents/mcp-bridge/constellation.html',encoding='utf-8').read(); m=re.search(r'<script>\n(.*?)</script>', h, re.S); open('_const_check.js','w',encoding='utf-8').write(m.group(1))"
node --check _const_check.js && echo "SYNTAX OK" && rm _const_check.js
```
Expected: `SYNTAX OK`. If `node` is not on PATH, note it and fall back to `python -c "import ast"` is not valid for JS — instead load the page and check the browser console has no errors (record which you did). Do NOT commit `_const_check.js`.

- [ ] **Step 6: Manual check**

`docker cp .agents/mcp-bridge/constellation.html agent-mcp-bridge:/app/constellation.html`, open `http://127.0.0.1:3302/constellation`:
- loads in **community** mode; ~11 clusters are distinctly coloured, most of the map is muted slate;
- click the toggle → nodes transition to note/skill/code colours, label reads `colour · layer`;
- click again → back to community colours.
Record what you saw in the report.

- [ ] **Step 7: Commit**

```bash
git checkout HYPERFOCUS_ZONE/06-AI-Context/graph.json HYPERFOCUS_ZONE/06-AI-Context/embeddings.json 2>/dev/null || true
git add .agents/mcp-bridge/constellation.html
git commit -m "feat(constellation): community colouring + colour-mode toggle

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_012RjkCXg6AFBdQaUbtoW6Nf"
```

---

## Task 2: Mode-swapped legend + community focus + tooltip/panel

**Files:**
- Modify: `.agents/mcp-bridge/constellation.html` (inline `<script>`)

**Interfaces:**
- Consumes from Task 1: `colorMode`, `communityColor`, `communityColorMap`, `commSize`, `realComms`, `MUTED`, `fillFor`, `setMode`, `#modeToggle`.
- Consumes existing: `counts`, `COLORS`, `visible` (`{note,skill,code,dead}` bools), `node`/`label`/`link` selections, `focus()`, `unfocus()`, `pinned`, `#legend`, `#tip`, `openPanel`.
- Produces: `focusedComms` (`Set<string>` of community ids, plus the sentinel `"__isolated__"`), `applyCommunityFocus()`, `renderLegend()`. Task 1's `setMode` already references `focusedComms`/`renderLegend` behind `typeof` guards — those become live here.

- [ ] **Step 1: Add `focusedComms` + `applyCommunityFocus()` — near `let pinned = null;`**

Right after `let pinned = null;` (currently ~line 226):

```js
  const focusedComms = new Set();              // community ids (+ "__isolated__" sentinel)
  const isMuted = d => !communityColorMap.has(d.community);
  const litByComm = d =>
    focusedComms.has(d.community) ||
    (focusedComms.has("__isolated__") && isMuted(d));

  function applyCommunityFocus() {
    if (focusedComms.size === 0) { unfocus(); return; }
    const lit = new Set(nodes.filter(litByComm).map(n => n.id));
    node.transition().duration(150).attr("fill-opacity", n => lit.has(n.id) ? 1 : 0.12);
    label.transition().duration(150).attr("opacity", n => lit.has(n.id) ? 1 : 0.15);
    link.transition().duration(150)
      .attr("stroke-opacity", l => (lit.has(l.source.id) || lit.has(l.target.id)) ? 1 : 0.15);
  }
```

- [ ] **Step 2: Make `unfocus()` focus-set-aware**

Current `unfocus()` (~line 238) is:

```js
  function unfocus() {
    if (pinned) return;
    node.transition().duration(150).attr("fill-opacity", 0.85);
    link.transition().duration(150).attr("stroke-opacity", 1)
      .attr("stroke", l => edgeColor(l.type));
    label.transition().duration(150).attr("opacity", 1);
  }
```

Replace the body so a non-empty `focusedComms` is the resting state:

```js
  function unfocus() {
    if (pinned) return;
    link.transition().duration(150).attr("stroke", l => edgeColor(l.type));
    if (focusedComms.size > 0) { applyCommunityFocus(); return; }
    node.transition().duration(150).attr("fill-opacity", 0.85);
    link.transition().duration(150).attr("stroke-opacity", 1);
    label.transition().duration(150).attr("opacity", 1);
  }
```

(The `stroke` reset stays unconditional so hover edge-highlight always clears; the opacity restore is what defers to the community focus.)

- [ ] **Step 3: Replace the legend block with `renderLegend()`**

The current legend code (~lines 311-327, from `const legend = document.getElementById("legend");` through the end of the `forEach`) becomes a function. Keep `const visible = {…}` where it is (it's read by `setMode` and the search). Replace from `const legend = …` onward:

```js
  // ── legend (rebuilt per colour mode) ───
  const legend = document.getElementById("legend");
  legend.style.flexWrap = "wrap";
  legend.style.maxWidth = "min(60vw, 520px)";
  legend.style.justifyContent = "flex-end";

  function chip(dotColor, name, count, extra) {
    const el = document.createElement("div");
    el.className = "chip";
    el.innerHTML = `<span class="dot" style="background:${dotColor}"></span>${name} <span class="n">${count}</span>`;
    if (extra) el.title = extra;
    legend.appendChild(el);
    return el;
  }

  function renderLegend() {
    legend.innerHTML = "";
    if (colorMode === "layer") {
      [["note","notes"],["skill","skills"],["code","code"],["dead","dead"]].forEach(([g, nm]) => {
        if (!counts[g]) return;
        const c = chip(COLORS[g], nm, counts[g]);
        c.classList.toggle("off", !visible[g]);
        c.onclick = () => {
          visible[g] = !visible[g];
          c.classList.toggle("off", !visible[g]);
          node.attr("display", n => visible[n.g] ? null : "none");
          label.attr("display", n => visible[n.g] ? null : "none");
          link.attr("display", l => (visible[l.source.g] && visible[l.target.g]) ? null : "none");
        };
      });
      return;
    }
    // community mode — focus toggles
    realComms.forEach(([id, cnt], i) => {
      if (i >= PALETTE.length) return;
      const member = nodes.find(n => n.community === id);
      const label_ = (member && member.community_label) || id;
      const c = chip(communityColorMap.get(id), label_, cnt, id);
      c.classList.toggle("off", focusedComms.size > 0 && !focusedComms.has(id));
      c.onclick = () => { toggleComm(id); };
    });
    const isoCount = nodes.filter(isMuted).length;
    if (isoCount) {
      const c = chip(MUTED, "isolated", isoCount, "singletons + tail communities");
      c.classList.toggle("off", focusedComms.size > 0 && !focusedComms.has("__isolated__"));
      c.onclick = () => { toggleComm("__isolated__"); };
    }
  }

  function toggleComm(key) {
    focusedComms.has(key) ? focusedComms.delete(key) : focusedComms.add(key);
    renderLegend();               // refresh the .off dimming on chips
    applyCommunityFocus();
  }

  renderLegend();
```

- [ ] **Step 4: Clear `focusedComms` on empty-space click**

The `svg.on("click", …)` handler (~line 258) currently does `pinned = null; unfocus(); closePanel();`. Add the clear:

```js
  svg.on("click", () => { pinned = null; focusedComms.clear(); renderLegend(); unfocus(); closePanel(); });
```

Also add it to the `Escape` keydown handler (~line 307) and `#panelClose` onclick (~line 306) so those paths stay consistent — change each `pinned = null; unfocus(); closePanel();` to also `focusedComms.clear(); renderLegend();` **only** in the `svg` empty-click and `Escape` paths (leave `#panelClose` as just closing the panel — closing the detail panel should not wipe a community focus). Final: `svg` click and `Escape` clear the focus; `panelClose` does not.

- [ ] **Step 5: Tooltip + panel community lines**

Tooltip (`node.on("mouseover")`, ~line 248):

```js
      tip.innerHTML = `${(d.label || d.id)} <span class="layer">· ${d.layer}` +
        `${d.community ? " · " + (d.community_label || d.community) : ""}</span>`;
```

Panel meta (`openPanel`, the array at ~line 286-292) — add one entry:

```js
      d.community && `community <b>${d.community_label || d.community}</b> · <b>${commSize.get(d.community) ?? 1}</b> nodes`,
```

- [ ] **Step 6: Syntax gate + manual check**

Same extraction + `node --check` as Task 1 Step 5. Then `docker cp` and verify on `http://127.0.0.1:3302/constellation`:
- community mode: one chip per cluster + an `isolated` chip; chips wrap, right-aligned;
- click the largest chip → that cluster stays full-opacity, everything else dims; click a second chip → both lit (union); click a lit chip → it dims;
- click the `isolated` chip → the 105 singletons light, clusters dim;
- click empty space → all restored; chips un-dim;
- hover a clustered node while a community is focused → transient neighbour-focus, then mouseout returns to the community-focused state (not full opacity);
- toggle to layer mode → community focus cleared, 4 layer chips back, hide toggles work; toggle back → clean community mode.

- [ ] **Step 7: Commit**

```bash
git checkout HYPERFOCUS_ZONE/06-AI-Context/graph.json HYPERFOCUS_ZONE/06-AI-Context/embeddings.json 2>/dev/null || true
git add .agents/mcp-bridge/constellation.html
git commit -m "feat(constellation): community focus legend + tooltip/panel community lines

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_012RjkCXg6AFBdQaUbtoW6Nf"
```

---

## Task 3: Static structure test + handover note

**Files:**
- Create: `tests/test_constellation_page.py`
- Create (or append): `NEXT_SESSION_HANDOVER_2026-09-03.md`

**Interfaces:**
- Consumes: the finished `.agents/mcp-bridge/constellation.html` from Tasks 1-2.
- Produces: a committed regression lock. This is a **structure/regression test, not TDD** — a D3 viz has no runtime assertions worth writing here; its behaviour was verified by the manual checklists. The test's job is to fail loudly if a future edit deletes the community machinery or breaks the script's syntax.

- [ ] **Step 1: Write the test**

Create `tests/test_constellation_page.py`:

```python
"""Static structure lock for the constellation page's community colouring.

Not a behaviour test — a D3 force-graph is verified by eye (see the plan's
manual checklists). This guards against a future edit silently removing the
v5 community machinery or landing a JS syntax error in the inline script.
"""
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

PAGE = Path(__file__).resolve().parents[1] / ".agents" / "mcp-bridge" / "constellation.html"


def _script() -> str:
    html = PAGE.read_text(encoding="utf-8")
    m = re.search(r"<script>\n(.*?)</script>", html, re.S)
    assert m, "inline <script> block not found"
    return m.group(1)


def test_page_is_one_wellformed_html_doc():
    html = PAGE.read_text(encoding="utf-8")
    depth = 0
    worst = 0

    class P(HTMLParser):
        def handle_starttag(self, tag, attrs):
            nonlocal depth
            if tag not in ("br", "img", "meta", "link", "input", "hr"):
                depth += 1

        def handle_endtag(self, tag):
            nonlocal depth, worst
            if tag not in ("br", "img", "meta", "link", "input", "hr"):
                depth -= 1
                worst = min(worst, depth)

    P().feed(html)
    assert worst == 0, f"unbalanced tags (min depth {worst})"
    assert html.count("<script") == 2, "expected exactly 2 <script> tags (d3 CDN + inline)"


def test_inline_script_passes_node_check(tmp_path):
    if shutil.which("node") is None:
        import pytest
        pytest.skip("node not on PATH — JS syntax gate skipped")
    js = tmp_path / "const.js"
    js.write_text(_script(), encoding="utf-8")
    r = subprocess.run(["node", "--check", str(js)], capture_output=True, text=True)
    assert r.returncode == 0, f"node --check failed:\n{r.stderr}"


def test_community_machinery_present():
    s = _script()
    for ident in ("PALETTE", "MUTED", "communityColor", "communityColorMap",
                  "commSize", "realComms", "fillFor", "colorMode",
                  "focusedComms", "applyCommunityFocus", "renderLegend",
                  "community_label"):
        assert ident in s, f"missing identifier: {ident}"
    assert 'id="modeToggle"' in PAGE.read_text(encoding="utf-8")


def test_palette_shape():
    s = _script()
    m = re.search(r"const PALETTE = \[(.*?)\]", s, re.S)
    assert m, "PALETTE literal not found"
    hexes = re.findall(r'"(#[0-9a-fA-F]{6})"', m.group(1))
    assert len(hexes) >= 10, f"PALETTE has {len(hexes)} entries, want >= 10"
    assert hexes[:3] == ["#22d3ee", "#a78bfa", "#f59e0b"], "brand three must lead PALETTE"
    mm = re.search(r'const MUTED = "(#[0-9a-fA-F]{6})"', s)
    assert mm and mm.group(1).lower() not in [h.lower() for h in hexes], "MUTED must be distinct"


def test_no_regression_of_kept_features():
    s = _script()
    for ident in ("const COLORS", "const group", "const radius", "edgeColor",
                  "getElementById(\"search\")", "/graph/related/"):
        assert ident in s, f"spec 4.5 says this stays, but it's gone: {ident}"
```

- [ ] **Step 2: Run it**

```bash
cd "H:/HYPERFOCUSZONE/HperCore/BROski-Obsidian-Brain-for-HyperFocus-z0ne"
python -m pytest tests/test_constellation_page.py -q
```
Expected: 6 passed (or 5 passed + 1 skipped if `node` is not on PATH).

- [ ] **Step 3: Confirm the sibling test is untouched and green**

```bash
python -m pytest tests/test_constellation.py -q
```
Expected: 5 passed. If anything here changed, you edited the wrong file — revert.

- [ ] **Step 4: Full suite**

```bash
python -m pytest tests/ -q
```
Expected: 65 + (6 or 5) passed, no failures.

- [ ] **Step 5: Handover note**

Create `NEXT_SESSION_HANDOVER_2026-09-03.md` (or append a `## 🟢 Completed` line if the file exists):

```markdown
# NEXT_SESSION_HANDOVER 2026-09-03

## 🟢 Completed 2026-09-03

- Constellation community colouring shipped (branch `constellation-community-coloring`).
  `:3302/constellation` now colours by Graph Brain v5 community with a
  `colour · community ⇄ layer` toggle (default community) and a click-to-focus
  community legend. One file: `.agents/mcp-bridge/constellation.html`.
- Spec: `docs/superpowers/specs/2026-09-03-constellation-community-coloring-design.md`
  Plan: `docs/superpowers/plans/2026-09-03-constellation-community-coloring.md`
- Deploy (post-merge): `docker cp .agents/mcp-bridge/constellation.html agent-mcp-bridge:/app/constellation.html`
  — FileResponse, no restart. Fold into the next image rebuild
  (HyperCode-V2.4 four-file compose + --profile brain-agents).
- `tests/test_constellation_page.py` added (static structure + node --check gate);
  `test_constellation.py` untouched.
```

- [ ] **Step 6: Commit**

```bash
git checkout HYPERFOCUS_ZONE/06-AI-Context/graph.json HYPERFOCUS_ZONE/06-AI-Context/embeddings.json 2>/dev/null || true
git add tests/test_constellation_page.py NEXT_SESSION_HANDOVER_2026-09-03.md
git commit -m "test(constellation): static structure lock + 2026-09-03 handover

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_012RjkCXg6AFBdQaUbtoW6Nf"
```

---

## Self-Review

**1. Spec coverage**

| Spec section | Task |
|---|---|
| §4.1 mode toggle, default community, reset-on-toggle | Task 1 Steps 1, 4 |
| §4.2 `PALETTE`/`MUTED`, ≥2-member filter, size-desc/id-asc sort, `communityColor` | Task 1 Step 2 |
| §4.3 layer legend unchanged; community chips as focus toggles; `isolated` chip; wrap/right-align; empty-space clears | Task 2 Steps 3, 4 |
| §4.3 community focused-set is the resting state; `focus()`/`unfocus()` read it | Task 2 Steps 1, 2 |
| §4.4 tooltip + panel `community_label` lines | Task 2 Step 5 |
| §4.5 untouched list (`radius`, `edgeColor`, forces, search, `/graph/related`) | Task 3 Step 1 `test_no_regression_of_kept_features` |
| §4.5 v4-graph safe (`communityColor` → `MUTED`, single `isolated` chip) | Task 1 Step 2 (`?? MUTED`), Task 2 Step 3 (`realComms` empty → only the `isolated` chip renders) |
| §5 data facts (11 real communities, palette has a spare slot) | inputs, not code |
| §6 new `tests/test_constellation_page.py`; `test_constellation.py` green | Task 3 Steps 1-3 |
| §6 manual checklist | Task 1 Step 6, Task 2 Step 6 |
| §7 deploy by `docker cp`, no restart | Task 1 Step 6, Task 2 Step 6, handover |
| §8 files touched (3) | File Structure table |
| §9 open questions (palette tuning, label collisions, chip overflow) | called out in Task 2 Step 6's manual check; palette hexes are in Task 1 Step 2 and tunable |

No gaps.

**2. Placeholder scan** — no "TBD"/"handle appropriately"/"similar to". Every code step has the literal code. The `setMode` `typeof` guards in Task 1 Step 4 are deliberate (so Task 1 is independently runnable before Task 2 defines `focusedComms`/`renderLegend`) and become live in Task 2 — noted inline, not a placeholder.

**3. Type consistency**

- `colorMode` — `let` string `"community"|"layer"`; read by `fillFor`, `setMode`, `renderLegend`. Consistent.
- `fillFor(d) -> hex` — Task 1 defines; used in the node `.attr("fill", …)`, `setMode` transition, panel badge. Same arity everywhere.
- `communityColorMap` — `Map<communityId, hex>`; `.get()` / `.has()` used; `communityColor` reads it; `renderLegend` reads it; `isMuted` uses `.has()`. Consistent.
- `commSize` — `Map<communityId, count>`; `.get()` in the panel meta line and `renderLegend`'s `realComms` derivation. Consistent.
- `realComms` — `Array<[id, count]>` sorted; iterated in `renderLegend` community branch with `[id, cnt]` and index `i`; `communityColorMap` built from `realComms.forEach(([id], i) => …)` in Task 1. Same shape both places.
- `focusedComms` — `Set<string>` (community ids + `"__isolated__"`); Task 1's `setMode` calls `.clear()` behind a `typeof` guard, Task 2 defines it and uses `.has()`/`.add()`/`.delete()`. Consistent.
- `renderLegend()` / `applyCommunityFocus()` / `toggleComm(key)` — no args except `toggleComm(key:string)`; defined Task 2, called from `setMode` (guarded), chip `onclick`, `svg` click, `Escape`. Consistent.
- `visible` — existing `{note,skill,code,dead}` bool map; `setMode` resets it, `renderLegend` layer branch reads it, search reads it. Unchanged shape.

No inconsistencies.
