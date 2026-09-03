# Deploy: Constellation community-colouring → baked agent-mcp-bridge image

## Outcome (2026-09-03 ~08:35)

Executed. Result:

- **FOLLOWUPS #1 + #7 landed**, 10/10 constellation tests green (38 across the wider community suite).
- **RAM fallback taken** — pre-flight showed free RAM 118 MB, swap 2021/2048 MB used, 58 containers; `pre-build-check.sh` line 50 memory gate is broken (`[: : integer expression expected`) and falsely reported "safe to build". Shipped via `docker cp .agents/mcp-bridge/constellation.html agent-mcp-bridge:/app/constellation.html`. **The baked image rebuild is still pending** — do it via the HyperCode-V2.4 four-file compose + `--profile brain-agents` when RAM allows.
- **Spec §6 click-through: 6/6 PASSED** on the deployed page (Playwright, 0 console errors) + FOLLOWUP #1 verified live. Stills: `HYPERFOCUS_ZONE/06-AI-Context/snapshots/2026-09-03-constellation-{community-coloring,layer-mode}.png`.
- **FOLLOWUPS #3 + #6 confirmed live and annotated** — open panel covers 11/12 legend chips; top-3 communities (113 nodes / 42%) render identical colours in both modes.
- **Pushed** to `origin/main` as `d0c3a64` (handover, `CLAUDE.md` Sacred Rule #8, docs, stills). `graph.json` auto-refresh churn was reverted, not committed.

The plan as written below is the pre-execution runbook; steps 2–3 (rebuild + baked-image verify) were deferred by the RAM fallback and remain the one open item.

## Outcome (2026-09-03 ~14:15) — BAKE LANDED ✅

The one open item is closed.

- **Baked** into `hypercode-v24-agent-mcp-bridge:latest` =
  `sha256:0e8693ac26e2883c53334d668fd48036b46e0b8f6aef66d129452d0829d9ccfb`
  (pre-build baseline was `sha256:3586c657731664746e9383dc12ef9f9eaea1e63c07906d55a2aa9a7d4b7e9e6c`),
  `--force-recreate`d, `restarts=0`.
- **RAM gate cleared by reversible teardown.** `docker stats` showed the real eaters
  were `grafana` (249 MB), `hypercode-core` (157, kept), `fcc-proxy` (139, kept),
  `grafana-agent`/`prometheus-cloud` (176), then a long tail of idle specialist agents.
  Stopped 32 (observability + grafana-cloud push agents + idle specialist agents);
  never touched `redis`/`postgres`/`data-net`, the 4 brain agents, `hyper-brain`, or
  `hypercode-core`. Post-teardown `wsl -e free -m`: **free 1155 MB, swap-used 792 MB**
  — both hard conditions PASS. Swap drained on its own (1795 → 792), so **no gate
  amendment was needed**. Restored all 32 with `docker start` afterward (list saved to
  the session scratchpad); 58 running, same as session start.
- **Build was cheap:** pip layer `CACHED` (`requirements.txt` untouched since
  2026-06-27), only the `COPY . .` layer rebuilt. No OOM, box stayed responsive.
- **Verified:** container `.Image` == fresh `docker images --no-trunc -q` == new digest,
  ≠ baseline; in-container `grep -c community` = 23, `grep -c node.interrupt` = 1,
  size 22586 B (== repo file); `/graph` v5 / 116 / greedy-modularity, 268 n / 482 e;
  `/graph/related/difficulty_dial` `related_by_community` len 4; `/constellation`
  serves `community` ×23; the 3 sibling brain agents + `hyper-brain` untouched
  (`restarts=0`).
- **FOLLOWUP #3 still recapture: not done** — no browser this session (Chrome
  extension not connected, Playwright MCP down). In-container file byte-identical to
  the one screenshotted this morning ⇒ layout unchanged; the existing still stands.
  Grab the panel-open still opportunistically next browser-capable session.
- **Pre-existing (not bake-caused):** observability `prometheus` and grafana-cloud
  `prometheus-cloud` share volume `hypercode-v24_prometheus-data` → TSDB lock
  contention; the observability one crash-loops (`lock DB directory: resource
  temporarily unavailable`). It was already `0B/0B` at session start. Give them
  separate volumes or run only one — ~15 min, its own task.

## Next-session bake checklist — ✅ DONE 2026-09-03 ~14:15 (kept below for the record)

> ⚠️ **Until the bake lands, do not `--force-recreate` `agent-mcp-bridge` or restart the stack.** The live page is a `docker cp` overlay — any recreate silently reverts it to the pre-feature `constellation.html`. If it does get wiped: `docker cp .agents/mcp-bridge/constellation.html agent-mcp-bridge:/app/constellation.html` from the Brain repo, then bake.

1. **Quiet-box gate (numeric, not vibes).** `wsl -e free -m` → proceed only if **`free` ≥ 900 MB AND swap-used < 1024 MB (< 50%)**. (WSL total is ~3.9 GB on this box — `.wslconfig` 4 GB cap, never raise it — so "free > 4 GB" is impossible; 900 MB free + swap under half is the real "quiet" bar.) If under: stop `--profile observability` + any idle agents, or wait. Ignore `pre-build-check.sh`'s verdict — its line-50 memory gate is broken.
2. **Baseline.** `docker inspect agent-mcp-bridge --format '{{.Image}}'` → record the id.
3. **Build + recreate** from `H:\HYPERFOCUSZONE\HperCore\HyperCode-V2.4`:
   ```
   docker compose -f docker-compose.yml -f docker-compose.secrets.yml -f docker-compose.registry.yml -f docker-compose.hyperhealth.yml --profile brain-agents build agent-mcp-bridge
   docker compose -f docker-compose.yml -f docker-compose.secrets.yml -f docker-compose.registry.yml -f docker-compose.hyperhealth.yml --profile brain-agents up -d --no-deps --force-recreate agent-mcp-bridge
   ```
   `requirements.txt` is unchanged → pip layer should cache-hit → only the `COPY . .` layer rebuilds (fast, low RAM). Do NOT pass `--remove-orphans`.
4. **Verify the bake took:**
   - container `.Image` == `docker images hypercode-v24-agent-mcp-bridge:latest -q` (fresh), ≠ step-2 baseline
   - `docker exec agent-mcp-bridge grep -c community /app/constellation.html` → **23**
   - `docker exec agent-mcp-bridge grep -c node.interrupt /app/constellation.html` → **1**
   - `curl -s http://127.0.0.1:3302/graph` → `meta` v5 / 116 / greedy-modularity; `/graph/related/difficulty_dial` non-empty `related_by_community`
   - `docker ps` → `hyper-brain` + the other 3 brain agents untouched
5. **Re-capture the FOLLOWUP #3 evidence still** while the page is up (Playwright is wired; other stills are in `06-AI-Context/snapshots/`): panel-open state → `06-AI-Context/snapshots/2026-09-03-constellation-panel-covers-legend.png`.
6. **Flip the record** — `NEXT_SESSION_HANDOVER_2026-09-03.md` and `brain-graph-memory-hub.md`: "STILL PENDING" → "baked + confirmed `<image-id>` `<date>`".
7. **`git fetch` → commit → push** (Brain repo). Then the deploy is genuinely done.

### FOLLOWUP #6 — ship decision (closed, not deferred)

**Decision 2026-09-03: SHIPPED with mono-mega-communities.** The top-3 communities (46/38/29 nodes = 42%) wear the brand three (`#22d3ee`/`#a78bfa`/`#f59e0b`) in *both* modes, so the toggle's "see the map differently" promise is muted for ~42% of the graph. Accepted because: the other 58% genuinely re-reads, and community focus/dim works regardless of colour — a legitimate ship state, documented. **Open work tracked as FOLLOWUP #6:** a size-aware sub-assignment of `PALETTE[0..2]` to distinct-but-harmonious hues for the 3 biggest communities (keep brand harmony + muted-tail contrast). ~1 hr, batchable with the bake session as a `design-brain` pass. Revisit then; do not leave it nagging past that.

## Context

The `constellation-community-coloring` feature is **already built, tested, merged to `main`, and pushed** in the Brain repo (`BROski-Obsidian-Brain-for-HyperFocus-z0ne`, merge `3e79136`). The whole feature is one file: `.agents/mcp-bridge/constellation.html` — `:3302/constellation` now colours nodes by Graph Brain v5 community with a `colour · community ⇄ layer` toggle (default community) and a click-to-focus community legend. ~70 tests green.

What is **not** done is the deploy. The live `agent-mcp-bridge` container runs image `hypercode-v24-agent-mcp-bridge:latest` built 2026-09-02 23:11 — that image baked v5 graph code (`graph_builder.py` / `communities.py` / `mcp_bridge.py`) but its `constellation.html` predates the community-colouring feature (merged 2026-09-03). Any current parity on the live page is a `docker cp` hot-patch overlay that **reverts on the next `--force-recreate`**. Commit `e0ba3c4` already records the correct fix: bake it into the image. This plan closes that loop, verifies the baked image is actually live, runs the spec §6 manual click-through once (no browser was available during the build), records the deploy as done, and adds a Sacred Rule so the `docker cp` revert-trap can't bite again.

Two of the 7 deferred FOLLOWUPS items get folded in because they are two-minute fixes: **#1** (`node.interrupt()` on search-clear) and **#7** (stale test literal in a plan doc). The other 5 stay deferred.

## Decisions (resolved)

1. **Click-through** — Claude drives the 6 mechanical checks in Chrome + saves a GIF/still; Lyndz does the final aesthetic eyeball (colour, dim-focus feel, hover timing).
2. **FOLLOWUPS** — also land #1 and #7 in this pass; re-run `pytest` + `node --check`; fold into the same docs push. Items #2–#6 stay in the FOLLOWUPS doc.
3. **RAM fallback** — if pre-flight shows WSL RAM too tight for a safe build: `docker cp` the new `constellation.html` into the running container so the feature is live, leave the baked-rebuild **flagged as still-pending** in the handover, do **not** force a risky build.

## Key facts (from exploration)

- **Brain repo:** `H:\HYPERFOCUSZONE\HperCore\BROski-Obsidian-Brain-for-HyperFocus-z0ne` (own git repo, branch `main`). HperCore root is **not** a git repo.
- **Changed file:** `.agents/mcp-bridge/constellation.html` (458 lines, `grep -c community` → **23**). In-container path `/app/constellation.html`, served by FastAPI `FileResponse`, re-read per request (no restart needed on file swap).
- **Service:** `agent-mcp-bridge`, defined only in `H:\HYPERFOCUSZONE\HperCore\HyperCode-V2.4\docker-compose.brain.yml` (pulled into root `docker-compose.yml` via `include:`), profile `["brain-agents"]`, `container_name: agent-mcp-bridge`, no `image:` key → image name `hypercode-v24-agent-mcp-bridge:latest`, port `127.0.0.1:3302:3302`.
- **Dockerfile:** `.agents/mcp-bridge/Dockerfile` — `FROM python:3.12-slim` / `COPY requirements.txt .` / `pip install` / `COPY . .`. `requirements.txt` is unchanged since the last build → the pip layer should cache-hit and the rebuild should be just the fast `COPY . .` layer.
- **Rebuild command (on record in `NEXT_SESSION_HANDOVER_2026-09-02.md`):**
  ```
  cd H:\HYPERFOCUSZONE\HperCore\HyperCode-V2.4
  docker compose -f docker-compose.yml -f docker-compose.secrets.yml -f docker-compose.registry.yml -f docker-compose.hyperhealth.yml --profile brain-agents build agent-mcp-bridge
  docker compose -f docker-compose.yml -f docker-compose.secrets.yml -f docker-compose.registry.yml -f docker-compose.hyperhealth.yml --profile brain-agents up -d --no-deps --force-recreate agent-mcp-bridge
  ```
  `--no-deps` keeps `hyper-brain` + the other 3 brain agents untouched. The "orphan containers" warning is **expected** with a partial file set — do **not** pass `--remove-orphans`.
- **Pre-build guard:** `H:\HYPERFOCUSZONE\HperCore\HyperCode-V2.4\scripts\pre-build-check.sh` (disk `MIN 15GB` / RAM `MIN 1024MB`). The compose `build` path does **not** run it automatically — must invoke manually.
- **RAM ceiling** (`hyperfocuszone-8gb-ram-ceiling` memory): the 2026-09-02 rebuild ran with ~150 MB RAM free and "the box survived" — tight. Never raise `.wslconfig`. Never build while the stack is under heavy load.
- **Verify recipe (on record):** `curl :3302/graph` → `meta.version 5`, `communities_count 116`, `community_algo greedy-modularity`.

## Plan

### 0. Land the two cheap FOLLOWUPS (before the build, so the image bakes them in)

- **#1 — search-clear vs running transition** (`.agents/mcp-bridge/constellation.html`): add `node.interrupt()` at the top of the **non-empty-query** branch of the `#search` input handler, so a fresh keystroke cancels an in-flight 150 ms `applyCommunityFocus()` transition before it overwrites the search opacities.
- **#7 — stale test literal** (`docs/superpowers/plans/2026-09-03-constellation-community-coloring.md`, Task 3 Step 1): change `assert "function group" in s` → `assert "const group" in s` to match the committed test / source (`const group = l => …`). Doc-only.
- Guard: `cd H:\HYPERFOCUSZONE\HperCore\BROski-Obsidian-Brain-for-HyperFocus-z0ne && pytest tests/test_constellation_page.py tests/test_constellation.py -q` (node --check gate runs inside `test_inline_script_passes_node_check`). Both must stay green.
- Mark #1 and #7 done in `docs/superpowers/plans/2026-09-03-constellation-community-coloring-FOLLOWUPS.md`.

### 1. Pre-flight (read-only, ~1 min)

- `docker context show` → must be `desktop-linux`.
- `docker system df` and `wsl -e free -m` (or `bash H:\HYPERFOCUSZONE\HperCore\HyperCode-V2.4\scripts\pre-build-check.sh`) → confirm ≥15 GB disk and comfortably more than 1 GB RAM free. **If RAM is tight:** `docker cp .agents/mcp-bridge/constellation.html agent-mcp-bridge:/app/constellation.html` from the Brain repo root (live immediately, no restart), leave the baked rebuild flagged pending in the handover, skip steps 2–3, still do steps 4–6.
- `docker inspect agent-mcp-bridge --format '{{.Image}}'` → record the **current** image ID (baseline for the "did the rebuild take" check).
- Confirm the working tree in the Brain repo is clean and on `main` at `3e79136` (or later): `git -C H:\HYPERFOCUSZONE\HperCore\BROski-Obsidian-Brain-for-HyperFocus-z0ne status` / `log --oneline -3`.

### 2. Rebuild + force-recreate

- Run the manual `pre-build-check.sh` first (guard the compose build path that skips it).
- Run the two `docker compose` commands above verbatim from `H:\HYPERFOCUSZONE\HperCore\HyperCode-V2.4`.
- Expect a fast build (pip layer cache-hit; only the `COPY . .` layer rebuilds).

### 3. Verify the baked image is actually live (not a docker cp overlay)

- `docker images hypercode-v24-agent-mcp-bridge:latest -q` and `docker inspect agent-mcp-bridge --format '{{.Image}} {{.Created}}'` → the container's `.Image` must equal the freshly-built image ID, and differ from the step-1 baseline.
- `docker exec agent-mcp-bridge grep -c community /app/constellation.html` → **23** (proves the new file is in the container filesystem; combined with the fresh image ID above, proves it's baked, not `docker cp`-ed).
- HTTP smoke:
  - `curl -s http://127.0.0.1:3302/constellation | grep -c community` → 23
  - `curl -s http://127.0.0.1:3302/constellation | grep -o "colour . community"` → toggle markup present
- Regression (v5 graph endpoints unchanged):
  - `curl -s http://127.0.0.1:3302/graph` → `meta`: `version 5`, `communities_count 116`, `community_algo greedy-modularity`
  - `curl -s "http://127.0.0.1:3302/graph/related/difficulty_dial?limit=4"` → non-empty `related_by_community`
- `docker compose ps agent-mcp-bridge` → `running (healthy)`; `docker ps` → other 3 brain agents + `hyper-brain` untouched.

### 4. Manual click-through — spec §6 checklist (one-time, on the deployed page)

Load `http://127.0.0.1:3302/constellation` (invoke the `claude-in-chrome` skill first, then drive it; page is loopback-only, Chrome on the Windows host reaches it). Record a GIF (`constellation_community_clickthrough.gif`) + one still for the vault. Mechanical checklist:

1. Mode toggle `community → layer → community` — via click **and** keyboard (`#modeToggle` has `role="button"` / Enter / Space).
2. Community legend chip: click to focus (rest of graph dims via `applyCommunityFocus`), click again to un-focus.
3. Isolated / muted singletons: `isolated` chip + `MUTED` (`#4b5563`) styling render correctly.
4. Pin a node, then focus a community — **pinned node yields to community focus** (the `c42c488` fix).
5. Search a node → clear the box → an active community focus is **restored**, not lost (the `71c6756` fix).
6. Hover tooltip + open side panel → `community_label` / member-count lines present.

Also re-check item **#1** here: focus a community, type in search, clear it mid-transition, type again — the graph should land on search opacities, not flash to community-focus opacities.

Then hand the page to Lyndz for the aesthetic sign-off (colour perception, dim-focus feel, hover timing) — a human call.

### 5. Record the deploy as done

- `NEXT_SESSION_HANDOVER_2026-09-03.md` — replace the "Deploy (post-merge): `docker cp` … Fold into the next image rebuild" line with: baked into `hypercode-v24-agent-mcp-bridge:latest` (`<image-id>`) on 2026-09-03, `--force-recreate`d, click-through passed (link the GIF).
- `CLAUDE.md` ("Sacred Rules — Obsidian Brain" table) — add row 8:
  `**`agent-mcp-bridge` / `constellation.html` changes = rebuild the image (HyperCode-V2.4 four-file compose + `--profile brain-agents`), NEVER `docker cp`** | `docker cp` overlays silently revert on any `--force-recreate`; the image is the source of truth (`e0ba3c4`)`
- User auto-memory: update `C:\Users\Lyndz\.claude\projects\H--HYPERFOCUSZONE-HperCore\memory\brain-graph-memory-hub.md` — flip "Constellation community colouring … PENDING proper rebuild + manual click-through" to done/verified with date; update its one-line pointer in `MEMORY.md`.

### 6. Push (Brain repo only)

The merged `constellation.html` from `3e79136` is already on `origin`. This push carries: the **#1** `node.interrupt()` fix in `constellation.html`, the **#7** doc-literal fix, the FOLLOWUPS doc (#1/#7 marked done, #3/#6 annotated with what the click-through showed), the updated handover, and the new `CLAUDE.md` Sacred Rule.

```
git -C H:\HYPERFOCUSZONE\HperCore\BROski-Obsidian-Brain-for-HyperFocus-z0ne fetch origin
git -C ...Brain... add .agents/mcp-bridge/constellation.html \
  docs/superpowers/plans/2026-09-03-constellation-community-coloring.md \
  docs/superpowers/plans/2026-09-03-constellation-community-coloring-FOLLOWUPS.md \
  NEXT_SESSION_HANDOVER_2026-09-03.md CLAUDE.md
git -C ...Brain... commit    # message + Co-Authored-By / Claude-Session trailer
git -C ...Brain... push origin main
```

(`git fetch` before push — Sacred Rule; origin can move under the parallel auto-commit workflow. Commit directly on `main`: these are the non-blocking residuals the merge review already cleared, not a new feature.)

### 7. Annotate the remaining 5 FOLLOWUPS

In `docs/superpowers/plans/2026-09-03-constellation-community-coloring-FOLLOWUPS.md`, from what the click-through showed on the deployed page, add a one-line observation under:
- **#3** — does an open side panel actually cover the wrapping community legend at the current graph size?
- **#6** — do the 3 biggest communities (46/38/29 nodes) look identical in `community` vs `layer` mode, making the toggle read as "nothing changed"? If yes, flag as the next `design-brain` pass.
Items #2, #4, #5 stay untouched (out of visual reach / larger changes).

## Verification (end-to-end)

- `pytest tests/test_constellation_page.py tests/test_constellation.py -q` green after the #1 edit (node --check gate included).
- Build succeeds without OOM; box stays responsive. (RAM-fallback path: `docker cp` overlay live, rebuild flagged pending.)
- Container `.Image` == freshly-built image ID (≠ pre-build baseline); `docker exec agent-mcp-bridge grep -c community /app/constellation.html` == 23.
- `curl :3302/constellation` serves the new page; `curl :3302/graph` still reports `version 5` / `communities_count 116` / `community_algo greedy-modularity`; `/graph/related/difficulty_dial` still returns non-empty `related_by_community`.
- Other 3 brain agents + `hyper-brain` still running (`--no-deps` respected).
- All 6 click-through interactions + the #1 re-check behave as specced; GIF + still saved for the vault.
- Handover + `CLAUDE.md` Sacred Rule + auto-memory (`brain-graph-memory-hub.md` + `MEMORY.md` pointer) updated.
- FOLLOWUPS doc: #1/#7 marked done, #3/#6 annotated.
- `git fetch` then docs+fix commit pushed to `origin/main` (Brain repo); commit carries the `Co-Authored-By` / `Claude-Session` trailer.
