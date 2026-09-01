# Technical Assessment: HyperCode-V2.4 — Revision 2

**Date:** 2026-08-30 (Rev 2, same day as Rev 1)
**Supersedes:** Rev 1, retained as the record of the correction chain
**Evidence base:** repository at commit `53e3d42` (GitHub API structural inspection + commit `bc96d441` history), operator runtime observations (2026-08-30 session), operator clone inspection (HEAD `53e3d42`)

---

## 0. Revision Log

- **Withdrawn — Rev 1 §4.1.** Rev 1 asserted "no `safety_gate.py` exists in any welshDog repository." False. `agents/crew-orchestrator/safety_gate.py` exists (4,532 bytes; exactly 142 lines, created in commit `bc96d441`, 2026-07-12: *"Add crew-orchestrator safety gate to gate agent dispatch via Safety Shepherd in monitor/enforce modes"*). It sits on the live dispatch path (`crew-orchestrator/main.py:533–541`). Rev 1's negative was a GitHub code-search index false negative laundered into a factual claim — the exact failure mode Rev 1 was written to guard against.
- **Counter-correction to the rebuttal.** The rebuttal's table states the gate has "no tests." Also false at the artifact level: `agents/crew-orchestrator/tests/test_safety_gate.py` exists at HEAD (4,270 bytes; 113 lines, added in the same commit `bc96d441`). And `agents/fleet-controller/tests/test_safety_unavailable.py` (2,629 bytes) plus `test_no_execution.py` (1,972 bytes) mean the fail-closed contract tests the rebuttal recommended *building* already exist for the strict client. See §2.
- **Promoted.** Port-8095 collision; dead Discord webhook; hourly interval → operator-observed-at-runtime (Class B).
- **Concessions recorded.** project-strategist dead-path claim withdrawn as stale (compose documents repoint to `./agents/08-project-strategist`); 199-node vault reclassified as doc-sourced (CLAUDE.md Graph Brain section), never counted.

## 1. Method (amended)

Evidence classes used throughout:

- **A — artifact-verified:** structural inspection via GitHub API at `53e3d42` (directory listings, commit history).
- **B — operator-observed-at-runtime:** live container/log observation, 2026-08-30, single observer.
- **C — clone-read:** operator inspection of a local clone at HEAD `53e3d42`.
- **D — doc-sourced:** project documentation, unverified.
- **E — open.**

**Method amendment.** GitHub code search is an index, not the artifact; it returns false negatives. Existence claims require a directory listing or clone. Negative existence claims require clone-based `git grep`. Rev 1 violated this rule; the violation is the documented cause of this revision.

## 2. The Safety Architecture — Corrected Picture

Three layers, each with artifact-verified test presence:

| Layer | File | Tests at HEAD | Behavior |
|---|---|---|---|
| Decision engine | `safety-shepherd/policy.py` | `test_policy.py` + `test_shepherd_service.py` (≈ 13.6 KB) [A] | Rule-ordered; default fallthrough → ALLOW [C] |
| Enforcement gate | `crew-orchestrator/safety_gate.py` (142 lines, `bc96d441`) | **`tests/test_safety_gate.py` (4,270 B)** [A] | Default mode `monitor` = records but always proceeds; fail-open on off-mode, HTTP errors, unreachable Shepherd [C] |
| Strict client | `fleet-controller/safety_client.py` | `test_safety_unavailable.py` (2,629 B), `test_no_execution.py` (1,972 B), `test_validation.py`, `test_hashing.py` [A] | No off/monitor/enforce modes, per its own docstring [C] |

**The decisive open question.** What does `crew-orchestrator/tests/test_safety_gate.py` actually assert? Both possibilities are artifact-consistent, and they imply different remediations:

1. It tests fail-closed semantics → the gate's fail-open defaults contradict its own suite; the fix is configuration.
2. It enshrines fail-open (asserts `skipped → ALLOW` on outage) → the suite is green because it pins the wrong contract. This is a stronger indictment than absent tests: it certifies the vulnerability.

Note the same caveat applies to `test_safety_unavailable.py`: its filename asserts its purpose, but its content is Class E from this review's position. The operator can close both questions in under a minute with a clone.

**The structural finding.** The correct enforcement semantics — strict client plus outage/unavailable contract tests — already exist in-repo, tested, in `fleet-controller/`. The gap is adoption, not construction: crew-orchestrator's dispatch path imports its own fail-open gate instead of the tested strict path.

## 3. Verified Deficiencies

Carried from Rev 1 unless noted [all Class A]:

- 38 compose files at root; `docker-compose.agents-full.yml` + `.backup` + `.backup2` committed; further `.backup`/`.bak`/`.new` variants in git.
- Manual, episodic audit cadence: dated HEALTH_CHECK artifacts and 8 session-handover files (2026-05-26 → 2026-08-19).
- Hygiene: empty `ls` and `vault` files committed at root; parallel `WHATSDONE.md` / `WHATS_DONE.md`.
- meta-research-architect: 7 modules ≈ 19 KB [A]. Scaffold defects enumerated by operator — missing `import os`, `logger.time()`, curl healthcheck in a slim image, 128 MB limit with sentence-transformers, unused `models.py`, invalid CORS combination, deprecated arXiv API [C]. "Never run" is inference, strongly supported: the compose `build:` context pointed at a nonexistent path, so nothing could have built [C].

Newly evidenced:

- **Port-8095 collision [B]:** `hyperhealth-api` bound `127.0.0.1:8095→8090`; `docker compose up meta-research-architect` failed with "port is already allocated"; relocated to 8101.
- **Dead webhook, wrong cadence [B]:** POST to `discord.com/api/webhooks/149475…` → HTTP 404; `RESEARCH_UPDATE_INTERVAL=3600` (hourly, not weekly) confirmed via `/status`. The briefs were firing hourly at a dead endpoint.

## 4. Claims Register (final state)

| # | Claim | State | Class |
|---|---|---|---|
| 1 | `safety_gate.py` fails open | Verified in code at `53e3d42` | A (existence, 142 lines, `bc96d441`) + C (behavior) |
| 2 | The gate has no tests | **Falsified** — `tests/test_safety_gate.py` at HEAD; contract direction open | A / E |
| 3 | Port-8095 collision | Confirmed at runtime | B |
| 4 | project-strategist dead path | Withdrawn (stale; repointed) | C |
| 5 | Dead webhook + hourly interval | Confirmed at runtime | B |
| 6 | 8 crash bugs in meta-research-architect | Confirmed as clone-read enumeration; "never run" strong inference | C |
| 7 | 199-node skills vault | Doc-sourced, never counted | D |
| 8 | Strict client exists | Confirmed; and it is tested | A |

## 5. Recommendations (Rev 2)

1. **Freeze the roster.** [unchanged]
2. **Close the enforcement gap (< 1 day).** Amended — the work is adoption, not construction:
   - First, read `crew-orchestrator/tests/test_safety_gate.py` and determine whether it pins fail-open or fail-closed. This 30-minute check decides the shape of everything below.
   - Point crew-orchestrator's dispatch path at the `fleet-controller` strict client (already written *and* tested — `test_safety_unavailable.py`, `test_no_execution.py`), or default `safety_gate.py` to `enforce` + fail-closed for infra-mutation callers.
   - Add or invert the contract tests at the gate: Shepherd outage → BLOCK; malformed verdict → BLOCK; monitor mode never reaches a mutation caller.
   - CI assertion: fleet-controller's rendered compose contains no `docker.sock` / `DOCKER_HOST` / `GITHUB_TOKEN`.
3. **"Does it even start" CI.** [unchanged; now backed by the runtime-confirmed 8095 collision]
4. **Definition of done, applied retroactively.** [unchanged; delete non-compliers]
5. **meta-research-architect consumer requirement.** [unchanged; urgency raised — hourly briefs to a dead endpoint]
6. **`.env` drift control.** [unchanged]
7. **Retire the "AGI-grade" label.** [unchanged]

## 6. Conclusion

Each document in this chain — the original critique, Rev 1, and the rebuttal — contained exactly one load-bearing error, and each error was caught by checking the artifact rather than trusting the previous layer. That is not the method failing; that is the method working. The corrected final picture: a tested decision engine; an enforcement gate that fails open by default but is *not* untested, with its test's contract direction the one remaining unknown; and a tested strict client already in-repo embodying the correct semantics. The remediation is now measured in hours: swap the dependency, verify the contract direction, pin it with CI.
