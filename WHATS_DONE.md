# ✅ WHATS_DONE — BROski-Obsidian-Brain

> Last synced: 2026-06-27 by BROski AI ⚡

## Done & Locked — Do NOT re-suggest

- Second Brain: PARA vault + GitHub bridge
- Obsidian sync integration with HyperCode-V2.4 documented
- .env files never committed to git
- Sacred import rules enforced across all linked repos
- **P2-3 Brain Levels 18 + 19 WIRED (2026-06-20)** — engine :8100.
  - L18 AI Distraction Filter: `distraction_monitor.py` connects SessionSnapshot → DistractionFilter → BROski nudge (Discord webhook `DISCORD_WEBHOOK_AIFS`). 3 signals: note activity (rapid switching), idle >15min, topic drift. Wired into `hyper_brain_core.py`: background loop (`DISTRACTION_MONITOR_INTERVAL_S`, only while session live) + `POST /distraction/check`. `_active_intent` captured at `/focus/start` for drift.
  - L19 DifficultyDial dynamic XP: `difficulty_dial.dynamic_multiplier` = intensity × session-quality × HyperSplit chunk-difficulty (`hyper_split.difficulty_score`, Level 17 bridge). `/focus/end` now applies the variable multiplier (replaces the flat one) before the economy POST. `/hypersplit` returns + stores `chunk_difficulty`.
  - 13 unit tests (`tests/test_brain_levels_18_19.py`). No new containers.
- **P2-2 Brain Constellation Level 20 (2026-06-20)** — `constellation_builder.py` now emits a real **graph** (`build_graph` → nodes = zone/engine/modules/repos/vault/economy, edges = real ecosystem wiring incl. cross-repo, no dangling) + auto-generates an **Obsidian Canvas** (`write_canvas` → `Hub/Brain-Constellation.canvas`, JSON Canvas, no orange). `GET /constellation/map` returns the graph JSON + writes note + canvas; new `POST /constellation/refresh` is the trigger target for the GitHub webhook / graph-refresh Action (engine :8100, no new container). Full topology = 23 nodes / 28 edges. 5 unit tests (`tests/test_constellation.py`).
- **Brain Level 21 — Sensory Accessibility / Bottleneck B7 (2026-06-27)** — `hyper-brain-themes.css` (root canonical → copied to `.obsidian/snippets/`): `@media (prefers-reduced-motion: reduce)` overload guard neutralising all 6 always-on animations; opt-in `body.sensory-low` (zero motion, no glows, desaturated) + `body.sensory-calm` (reduced motion, softer palette) profiles; reusable `body.dyslexia-support` class factored out of calm-mode/broski-zone. Closes the roadmap's last open bottleneck. Pure CSS, no rebuild. (commit 87f9a3c)
- **Brain dependency / security health pass (2026-06-27)** — all 5 `requirements.txt` bumped off early-2024 pins, headline **aiohttp 3.9.3 → 3.14.1** (closes request-smuggling/DoS/dir-traversal CVEs); FastAPI 0.110→0.138.1, pydantic 2.6.4→2.13.4, uvicorn/httpx/aiofiles/watchdog/pyyaml/dotenv current; redis kept on 5.x (5.3.1). Dockerfiles standardised `python:3.11→3.12-slim` (×5). Fixed a **latent undeclared `requests` dependency** (distraction_monitor.py imported it; added `requests==2.34.2`). 5 brain containers rebuilt via `--profile brain`, all endpoints (8100/3301/3302/3303/3304) green, aiohttp 3.14.1 confirmed inside, 21/21 unit tests pass, no OOM. (commit 87f9a3c)

## 🛡️ Ecosystem-wide Dependency / Security Audit — 2026-06-27

Full HperCore sweep (74 `requirements*.txt` scanned + `npm audit` across all Node repos). **Result: every repo at 0 known vulnerabilities, no accepted residuals.** Each change build/test-verified before push.

| Repo | What was done | Commit |
|---|---|---|
| BROski-Obsidian-Brain | Dep/security health pass + Level 21 (above) | 87f9a3c |
| WelshDog-Mission-Control | `npm audit fix` → 12 vulns (2 crit) **→ 0**; vite build green | eb9c613 |
| HyperCode-V2.4 (peripheral) | coderabbit-webhook + test-agent + hyperstudio reqs bumped (fastapi/pydantic/Pillow/multipart/requests); live `backend/` core was already clean | a021206 |
| BROskiPets-LLM-dNFT | fastapi 0.104.1→0.138.1, pydantic 2.5→2.13.4, requests 2.31→2.34.2 (+evolver); app imports clean (8 routes), web3/supabase left intact | ff12e8d |
| HyperAgent-SDK | `npm audit fix` 1 **→ 0** | 3753e88 |
| showcase-web | `npm audit fix` 7 (1 crit) **→ 0**; next build green | df93a70 |
| welshdog-designs-web3-shop | web3 wallet-tree: 52 **→ 0** via `ws`/`uuid` npm overrides (NOT a wagmi-3 migration; `--force` was destructive) | 49f7561 |
| Hyper-Vibe-Course / frontend | same `ws`/`uuid` overrides: 33 **→ 0** | af0e5ce |
| Hyperfocus-Home-Page | **Next 14.2.35 → 15.5.19** (closes 14 advisories incl. high DoS; async-request-api codemod, kept React 18) + postcss `$`-ref override + **replaced unmaintained gray-matter with the `yaml` pkg** (killed the last js-yaml DoS). 4 **→ 0**. Verified live on `welshdog.shop` (Vercel READY) | 61da393, 1a374e5 |

**Key lessons captured:** `npm audit fix --force` was actively destructive on web3 (wanted wagmi@0.12/viem@0.2 downgrades) — always trace the real root advisories (`via` leaves) first; the "web3 wallet-tree" scare was just 2 transitive leaves (`ws`, `uuid`). `HyperCode-V2.4/vault` is a **stale embedded clone of this Brain repo** — never commit/push from it.

## Sacred Rules (NEVER break)

- `.env` files — NEVER committed to git
- `from app.X import Y` — NEVER `from backend.app.X`
- Python indent — 4 spaces, NEVER 3, NEVER mixed
- Redis DB 1=cache, DB 2=rate limits. NEVER mix.
