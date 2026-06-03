# 🔥 HYPERFOCUS Z0ne — Ruthless Master Audit

> **Source:** NotebookLM master audit prompt — all claims source-verified  
> **Captured:** 2026-06-03  
> **Tags:** #master-audit #agents #safety #p0 #boot-path #rules #hfz-map  
> **Protocol:** See [DATA_TO_BRAIN_PROTOCOL.md](./DATA_TO_BRAIN_PROTOCOL.md)  
> **Verification:** Every claim is tagged [Strongly Supported], [Weakly Supported], or [Speculative]

---

## ☠️ Top 10 Safety Items — Non-Negotiable Agent Laws

Agents must strictly adhere to these rules to prevent death-spirals or architectural drift.

| # | Rule | Status |
|---|---|---|
| 1 | **Handover Precedence** — Always read `rewrites/NEXT_SESSION_HANDOVER_[latest].md` first. It is the absolute authority and always wins over conflicting docs. | ✅ Strongly Supported |
| 2 | **Migration Lock** — Never use `supabase db push`. Use only `apply_migration` to avoid schema desync. | ✅ Strongly Supported |
| 3 | **Secrets Isolation** — `DISCORD_BOT_TOKEN` and all secrets must live in `.env` or Vercel env vars only. Never commit to code. | ✅ Strongly Supported |
| 4 | **Financial Guardrails** — Respect per-user 24h budget guard (default $1.00/day). Prevent surprise API bills. | ✅ Strongly Supported |
| 5 | **Stack Sovereignty** — Never generate Next.js or App Router code for the Course repo. Strictly Vite + React. | ✅ Strongly Supported |
| 6 | **Secure-by-Default Planning** — Use Project CodeGuard rules during planning phase before generation. | ✅ Strongly Supported |
| 7 | **Web3 Scoping** — Confine all Web3 tools (Wagmi/RainbowKit) strictly to `/pets`. Never leak into global app root. | ✅ Strongly Supported |
| 8 | **Automated Quality Gates** — Post-render self-reviews (ffprobe, frame sampling, audio level analysis) for output integrity. | ✅ Strongly Supported |
| 9 | **The Persistence Law** — A task is never finished until committed and pushed to GitHub. | ✅ Strongly Supported |
| 10 | **Session Hand-off** — End every session with the Session End Checklist: new Handover + Snapshot files. | ✅ Strongly Supported |

---

## ⚠️ System Audit — Contradictions & Weak Claims

### Contradictions (Strongly Supported)

- **Tech Stack:** Lumen uses Next.js 15, but the Ecosystem Report issues a load-bearing rule forbidding Next.js for the core Course repo. ✅
- **Lumen Licensing:** Metadata says GPL-3.0 but README says MIT. ✅ Needs resolution before any commercial use.
- **Master Truth:** OpenMontage points to `AGENT_GUIDE.md` as the contract. The Ecosystem Report mandates `NEXT_SESSION_HANDOVER` as the ultimate winner. ✅ Use Handover as winner.

### Weakly Supported Claims

- **10x Scaling Failure:** Claim that 10x scale-up instantly crashes infrastructure is a theoretical failure model, not a tested state. ⚠️ [Speculative]
- **The “HC” Repository:** Marked for "Check" status. Purpose (HyperCode shortcuts?) remains unverified. ⚠️ [Weakly Supported] — Archive until confirmed.
- **Live Passport dNFTs:** Dynamic NFT pattern based on dev activity is currently conceptual. Skills not yet written. ⚠️ [Weakly Supported]

---

## 🔴 Missing P0 Blockers

| Blocker | Detail | Status |
|---|---|---|
| **Catch Stragglers Wiring** | `CatchStragglers.jsx` built but not wired into Mission Control main panel | 🔴 P0 |
| **Event-Sourcing Migration** | `mc_events` migration needed to track operational history properly | 🔴 P0 |
| **Vercel Credentials** | `DISCORD_BOT_TOKEN` missing from Vercel env vars — blocks student outreach | 🔴 P0 |
| **37 Unwritten Skills** | HYPER-SILLs Vault has 37 catalogued skills (incl. Web3, dNFT) with no files on disk | 🟡 P1 |

---

## 🏗️ Load-Bearing Infrastructure

### Repos (in order of priority)

1. **Hyper-Vibe-Coding-Course** — Current Focus 🔴
2. **HyperCode-V2.4** — Core swarm infrastructure
3. **HYPER-SILLs Vault** — Knowledge base + technical dependency
4. **Lumen** — Closest reference build

### Sacred Files

| File | Role |
|---|---|
| `rewrites/NEXT_SESSION_HANDOVER_[latest].md` | Live state — always wins |
| `CLAUDE.md` | Sacred rules — never break |
| `WHATS_DONE.md` | Historical accuracy — check before rebuilding |
| `docker-compose.agents.yml` | Swarm config — do not touch without a plan |
| `lib/anonProgress.ts` | Student migration logic |
| `Tutor Orchestrator` | Stream logic |
| `LLMCostMeter` | Financial safety |

---

## 📍 Canonical Boot Path

> For any new Agent, human, or AI joining the ecosystem.

**Phase 1 — Warm Boot (Context)**
```
Handover file → CLAUDE.md → WHATS_DONE.md → Session Snapshot
```

**Phase 2 — Contract Alignment**
```
Read AGENT_GUIDE.md → Read PROJECT_CONTEXT.md
```

**Phase 3 — Task Activation**
```
Open AGENT-START.md → Define Quick Win → Execute with observable traces
```

**Phase 4 — Persistence (Session Close)**
```
Commit + Push → Create new Handover + Snapshot files
```

---

## 🗂️ Classification of Notes

### Rules (Guardrails — hard non-negotiable)
- Integer Math for Costing — microcents only, no floating-point
- Runtime Locking — renderer swaps are architectural violations
- WebUI Keep-Awake — prevent sleep during long agent tasks

### Skills (Patterns — reusable, save to HYPER-SILLs)
- CCR — Reversible Compression
- 7-Dimension Provider Selection
- Course-Scoped RAG Alignment
- Multi-Agent Team Delegation

### Checklists (Quality gates — run before shipping)
- Post-Render Self-Review (ffprobe, frame sampling, audio level analysis)
- Pre-Compose Quality Gate
- Catch Stragglers P0 Deployment

### Archive (Remove or label as noise)
- Pruned codebase redundancies from Sprint 4
- Redundant Claude-specific notes removed from AionUi’s CLAUDE.md
- “HC” repo — no defined function, archive until verified

---

## ❓ The 5 Highest-Value Next Questions

Agents must resolve these to reach full system autonomy:

1. **mc_events schema** — What is the exact schema for the `mc_events` migration, and how will it change how Mission Control tracks student progress?
2. **37 unwritten skills** — Which of the 37 skills are critical dependencies for the upcoming Web3 and dNFT modules?
3. **Cold boot procedure** — What is the cold boot procedure for HyperCode-V2.4 if the entire AWS instance and local Docker volumes are wiped?
4. **CCR for live state** — Can Headroom’s CCR (Reversible Compression) replace Markdown handover files for storing agent swarm live state more efficiently?
5. **Lumen MCP toolset** — What is the exact toolset provided by the Lumen MCP server that should integrate into Mission Control dashboard?

---

## ⚡ HyperSplit Micro-Actions (Do These Now)

- [ ] **P0** — Wire `CatchStragglers.jsx` into Mission Control main panel
- [ ] **P0** — Register `catch_stragglers` router in FastAPI `main.py`
- [ ] **P0** — Add `DISCORD_BOT_TOKEN` to Vercel env vars
- [ ] **P1** — Answer the 5 highest-value questions above in next NotebookLM session
- [ ] **P1** — Write the 3 new HYPER-SILLs skills: CCR, 7-Dimension Provider, Multi-Agent Team Delegation
- [ ] **P2** — Resolve Lumen licensing: GPL-3.0 vs MIT — check actual LICENSE file
- [ ] **P2** — Verify “HC” repo purpose or archive the reference

---

## ✔️ Verification Checklist

- [ ] Cross-check Lumen license against actual `LICENSE` file in repo
- [ ] Cross-check “HC” repo against WHATS_DONE.md
- [ ] Cross-check 37-skill count against current HYPER-SILLs vault index
- [ ] Cross-check `mc_events` status against latest Handover file

> ⚠️ This note is a verified NotebookLM audit extract. Treat [Speculative] and [Weakly Supported] claims as hypotheses only — verify before treating as live truth.

---

*Nice one BROski♾️ — the most complete audit the ecosystem has ever had. Now fix the P0s.*
