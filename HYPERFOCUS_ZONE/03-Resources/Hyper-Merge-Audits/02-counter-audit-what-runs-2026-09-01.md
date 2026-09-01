# Hyper Merge — Independent Counter-Audit

**Date:** 2026-09-01
**Responds to:** `Hyper Merge Deep-Dive Audit – Academic + Ecosystem View.md` (Lyndz, same day)
**Sits in the chain with:** `academic-assessment-hypercode.md`, `academic-assessment-hypercode-rev2.md`
**Evidence base:** local clones at HEAD on `main` —
HyperCode-V2.4 `8839ae1b`, HyperAgent-SDK `046f1c0`, Hyper-Vibe-Coding-Course `65b8864`,
BROskiPets-LLM-dNFT `5cc6906`, BROski-Obsidian-Brain `35aa66f`, HYPER-SILLs `4f8c4a0`.
GitHub check history via `gh` (account `welshDog`, 2026-09-01).

---

## 0. What this audit is

Your audit inventories **what exists** across the five repos — the docs, the compose files, the
spec files, the culture. It is accurate as an inventory and I did not find a false claim of
existence in it.

This audit reports **what runs**. Same repos, different question. Where the two disagree, it is
because a file being present is not the same as the thing it describes being true.

### Evidence classes (inherited from the rev2 method)

| Class | Meaning |
|---|---|
| **A** | Artifact-verified — file read at the stated HEAD |
| **B** | Runtime-observed — `gh` check history, live output |
| **C** | Clone-read inference — behaviour read from source, not executed |
| **D** | Doc-sourced — taken from project docs, unverified |
| **E** | Open — not checked |

Every claim below carries a class. Items I did not verify are named in §6, not omitted.

---

## 1. Where I confirm your audit

- **Self-audit culture is real and it drove real fixes.** [A] The safety-card work
  (`agents/shared/safety_contract.py`, `crew-orchestrator/dispatch_capability.py`,
  `test_safety_client_mirrors_gate.py`) is new since rev2 and is a direct response to the
  rev1→rev2 critique. The loop from "audit finds gap" to "code closes gap" is functioning.
- **Doc redundancy is real.** [A] Quantified in §3.
- **SDK ↔ course spec alignment is not yet canonical.** [A] Confirmed, and it is an actual
  divergence, not just a drift risk — see §4.
- **CI is not reliably enforcing the safety/quality suite.** [B] Confirmed for HyperCode; more
  nuanced for Hyper-Vibe — see §2.

I did **not** verify your narrative-cohesion, sponsorship-dossier, or "GitHub Academic index"
points. They are reasonable editorial recommendations; they are outside what a clone can check,
so treat them as inherited [D], not endorsed.

---

## 2. CI: verified state, per repo

### HyperCode-V2.4 — every workflow on `main` fails at 0s [B]

`gh run list -R welshDog/HyperCode-V2.4 --branch main --limit 20` (push `8839ae1b`,
2026-09-01T13:36Z): **all 20 runs returned `completed / failure`, every one at `0s` duration**
(`conclusion: failure`, e.g. `tests.yml` run `33514354863`). Same pattern on the
`feature/kimi-k3-in-c` branch. A workflow that "fails" in zero seconds is not running your tests
and failing — it is failing to start (billing lock is the likely cause per session memory; also
possible: invalid workflow headers, missing permissions). The 36-workflow suite that both your
audit and mine point to as evidence of infra discipline is, at HEAD, an inventory of gates that
do not execute. This includes `agent-safety.yml`, `tests.yml`, `quality-gate.yml`,
`trivy-scan.yml`, `codeql.yml`.

### Hyper-Vibe-Coding-Course — deploy/security checks run; the project's own test suites do not [A][B]

More precise than "no CI." PR checks on `main` HEAD (`gh api .../check-runs`, `gh pr checks`):

- **Running and passing** [B]: Vercel (deployment completed), Supabase Preview, CodeRabbit,
  GitGuardian Security Checks, Vercel Preview Comments. So the repo does have a
  deploy + secret-scan + AI-review gate on PRs.
- **Not running** [A]: the repo's own test code. `frontend/tests/` holds 25 Playwright specs
  — including `stripe-checkout.spec.ts`, `auth.spec.ts`, `pets-mint-gate.spec.ts`,
  `supabase-browser-config.spec.ts`, `referral-rpc.spec.ts`;
  `agents/course-content-agent/src/tests/` holds TS unit tests. The only workflow that would run
  the Playwright suite,
  `frontend/.github/workflows/playwright.yml`, is **nested one directory below where GitHub
  Actions looks**. Actions reads `.github/workflows/` at the repo root only — root there
  contains just `FUNDING.yml`. So that workflow has never fired and cannot without being moved.
  [A][C]
- `gh run list` shows only `pages-build-deployment`, every run `failure`, nothing since
  2026-06-27. [B]

**Net:** the payment/auth-handling repo ships behind Vercel + GitGuardian + CodeRabbit, but its
functional and end-to-end test suites — the ones that would catch a broken checkout or a
regressed auth flow — have no runner.

### The other three — not run-checked [E]

- HyperAgent-SDK: single `ci.yml` [A].
- BROskiPets: `ci.yml` + `ci-cd.yml` [A].
- Obsidian-Brain: only `graph-refresh.yml` [A]; the Python brain modules have no test workflow.

**Severity:** high. A safety architecture that is not executed on every change is documentation.
HyperCode's gate suite is entirely red; Hyper-Vibe's own tests are unwired.

---

## 3. Doc sprawl, quantified

Tracked markdown, current HEAD, `git ls-files '*.md'` [A]:

| Repo | `.md` files | handover / status / health docs |
|---|---:|---:|
| HyperCode-V2.4 | 972 | 73 |
| Hyper-Vibe-Coding-Course | 642 | 16 |
| BROski-Obsidian-Brain | 218 | 25 |
| BROskiPets-LLM-dNFT | 115 | 6 |
| HyperAgent-SDK | 37 | 4 |
| **Total** | **~1,984** | **124** |

~2,000 tracked markdown files and 124 handover/status/health reports across five repos. Your
audit's "fragmented academic narrative" is correct; the number is the argument. The `academic-
assessment-hypercode` chain (original → rev1 → rebuttal → rev2) plus this file plus your Hyper
Merge audit are themselves six documents about the same system, none linked from any repo
README. The self-audit culture and the doc-sprawl problem are the same phenomenon.

---

## 4. SDK ↔ course spec — an actual divergence, not just a copy [A]

Your §"SDK and course alignment" is right to flag this. Full `diff` of
`HyperAgent-SDK/hyper-agent-spec.json` (5,126 B) against
`Hyper-Vibe-Coding-Course/hyper-agent-spec.json` (4,028 B):

- The **SDK spec is a superset**. It carries three things the course spec does not have at all:
  - a full **`web3` capability block** (spec v0.4.0+): `chain` enum, `token_standard`,
    `dnft` flag, `contract_address` pattern, on-chain `capabilities` enum
    (mint/evolve/transfer/burn/read-*), `signer_env_var`. This is the BROskiPets dNFT model.
  - a **`badges`** array (author-declared + registry-computed).
  - a JSON-Schema **`if`/`then` conditional** enforcing `port` required when
    `mcp_compatible: true`.
- The course spec collapses ~80 lines of the SDK spec into single lines and predates all of the
  above. It is a **stale earlier fork**, not a parallel dialect.
- One additional semantic drift on `mcp_compatible.description` (SDK: "port required, 3100-3999
  range"; course: "true only if the agent implements MCP SSE transport").

So the two agent frameworks in the merge are working from **different versions of the contract**,
and the course side cannot express Web3 agents at all. Recommendation: this is a real
reconciliation, not cosmetic — move the schema to the SDK as the single source, publish it,
have the course consume it with a pinned version, and regenerate any course agents against the
current shape.

---

## 5. The safety question rev2 left open — now closed [A]

Rev2 called this "the decisive open question": does
`agents/crew-orchestrator/tests/test_safety_gate.py` assert *Shepherd outage → BLOCK* or
*outage → ALLOW*?

**Answer: it asserts fail-open, and the picture is worse than that — in the shipped default
mode the gate does not enforce anything.** Read at HEAD `8839ae1b`:

1. **`test_safety_gate.py` certifies fail-open** [A]. Three tests assert it explicitly:
   `test_http_error_fails_open` → `ALLOW` on HTTP 500; `test_unreachable_shepherd_fails_open` →
   `ALLOW` on `ConnectionError`; `test_malformed_body_fails_open` → `skipped is True` on a
   non-dict body. Rev2's possibility #2 confirmed: the suite is green because it pins the wrong
   contract.

2. **The shipped default is `monitor`, which enforces nothing** [A].
   `safety_gate._mode()` defaults to `monitor` (`safety_gate.py:34`). `is_enforced()` returns
   true only for `mode == "enforce" and not skipped` (`safety_gate.py:115`). Both
   `docker-compose.core.yml:109` and `docker-compose.agents.yml:970` set
   `SAFETY_SHEPHERD_MODE=${SAFETY_SHEPHERD_MODE:-monitor}`. In `_safety_check_dispatch`
   (`main.py:524-610`, called on the live dispatch path at `main.py:813` and `:949`), the flow
   is: `decision = open_decision` from the fail-open gate → `if not is_enforced(...): return
   None`. In monitor mode `is_enforced` is always false, so **every verdict — including a clean
   BLOCK or ESCALATE from a healthy Shepherd — returns `None` (proceed).** Enforcement requires
   the operator to set `SAFETY_SHEPHERD_MODE=enforce`; whether Lyndz's `.env` does is [E].

3. **The fail-closed replacement exists and shadow-runs** [A]. `crew-orchestrator/safety_client.py`
   (sibling copy in `fleet-controller/`), each held to one spec by
   `agents/shared/safety_contract.py::assert_strict_client_contract`. Every failure branch
   (timeout, connect-error, non-200, malformed JSON, missing decision) returns the frozen
   `_FAIL_CLOSED` BLOCK singleton — contract-tested. `_safety_check_dispatch` runs it in
   parallel for the 10 mutation-capable agents in `dispatch_capability.json`
   (`project-strategist`, `backend-specialist`, `database-architect`, `devops-engineer`,
   `coder-agent`, …), compares verdicts, logs `Safety canary mismatch` / `match`, and
   **explicitly does not act on the strict result** (`main.py:561` comment).

**Net, at HEAD `8839ae1b`, on the live dispatch path:** with the shipped default config,
agent dispatch — including to mutation-capable executors — is not gated at all; a real BLOCK is
logged and ignored. Set `enforce` and it gates, but still fails open on any Shepherd error. The
fail-closed path that would fix both is built, contract-tested, and running in shadow, one
config flip away from being load-bearing. Rev2's "remediation measured in hours" holds: flip
`_safety_check_dispatch` to act on `closed_verdict` for `needs_strict` agents, confirm the
canary agrees, set `enforce`. Progress since rev2 (`safety_contract.py`, the mirror test,
capability roster) is genuine and is the audit loop working.

---

## 6. What I did not verify (class E — do not treat as cleared)

- Whether Lyndz's deployed `.env` sets `SAFETY_SHEPHERD_MODE=enforce`.
- Whether the `safety_client` canary is exercised at runtime (no live container this session).
- Whether HyperAgent-SDK `ci.yml` and BROskiPets `ci.yml` / `ci-cd.yml` pass.
- BROskiPets `SECURITY_AUDIT_REPORT` claims — not re-tested.
- Any Docker image actually builds. Rev2's runtime notes (port-8095 collision,
  meta-research-architect scaffold defects) not re-checked; assume still open.
- Obsidian-Brain brain-module endpoints (`:8100` / `:8101`) — not pinged.
- Your audit's "Longer-term academic moves" section — editorial, out of scope for a clone-read.

---

## 7. Recommendations, ranked by verified severity

1. **Get one required check green in each repo before adding anything.** [§2, high]
   HyperCode: diagnose why every workflow dies at `0s` on `main` (billing lock first) and get
   `tests.yml` running. Hyper-Vibe: move `frontend/.github/workflows/playwright.yml` to the
   repo root so the ~18 specs actually run on PRs. Until a repo has one green required check,
   its safety/quality docs are unenforced.

2. **Flip the safety gate off `monitor`, or set a date.** [§5, high]
   The fail-closed path is built and shadow-running. Either (a) make `_safety_check_dispatch`
   act on `closed_verdict` for `needs_strict` agents and set `SAFETY_SHEPHERD_MODE=enforce`, or
   (b) write down the canary-agreement threshold and the flip date. Shipping `monitor` as the
   default means agent dispatch is currently ungated by design.

3. **Reconcile `hyper-agent-spec.json`.** [§4, medium — real divergence, not cosmetic]
   One schema in the SDK, published, consumed by the course with a pinned version. The course
   copy predates the `web3` / `badges` / conditional-port additions and cannot describe Web3
   agents.

4. **Pick a canonical home for cross-repo reports and make the rest links.** [§3]
   Your recommendations #1–#3 (academic index, canonical health report, unified SPONSORS) are
   the right shape. Add an index entry for this audit chain itself, or it becomes the seventh
   unlinked document.

5. **Retire unverifiable superlatives.** [inherited from rev2 §5.7]
   "World's first neurodivergent-first autonomous AI infrastructure platform" is a claim a
   reviewer cannot check, and it undercuts the parts of the story that *are* verifiable — the
   audit culture, the safety-card loop, the self-correcting review chain.

---

## 8. Bottom line

Your audit is right that the ingredients are unusually strong: honest incident logs, a real
audit culture, neurodivergent-first intent in the code, a self-correcting review chain. Nothing
here contradicts that.

What a clone-read adds: the enforcement layer under all of it is thinner than the document count
implies.

- HyperCode's entire 36-workflow gate suite fails to start on every push to `main` (all 20
  most-recent runs `failure` at `0s`).
- Hyper-Vibe deploys behind Vercel/GitGuardian/CodeRabbit but never runs its own 25 Playwright
  specs (including `stripe-checkout` and `auth`), because the workflow file is in the wrong
  directory.
- The Safety Shepherd dispatch gate ships in `monitor` mode, where a clean BLOCK verdict is
  logged and ignored; the fail-closed replacement is built and shadow-running but not wired to
  act.
- The two agent frameworks use different versions of `hyper-agent-spec.json`.
- ~2,000 markdown files describe a system whose automated checks are, today, mostly red,
  misplaced, or set to observe-only.

The gap is not knowledge — all of this is diagnosed somewhere in the 124 status docs. The gap
is that diagnosis is not wired to enforcement. Three CI fixes and one config flip move the story
from "documented intentions" to "enforced guarantees."
