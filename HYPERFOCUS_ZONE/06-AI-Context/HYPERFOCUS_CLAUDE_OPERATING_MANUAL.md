# ⚡ HYPERFOCUS CLAUDE OPERATING MANUAL
### welshDog Edition — Built for Your Stack, June 2026
> Stop apologising for your brain. Start building.

---

## 🧠 THE GOLDEN RULE

**One Claude. One Job. One Window.**

> Chat = THINK → Cowork = SYNTHESISE → Code = BUILD

Never mix them. Never use Opus for a tiny question. Never use Chat for a refactor.

---

## 🗺️ DECISION MAP — Which Claude for What?

| Task Type | Use | Model |
|---|---|---|
| Brain dump, planning, specs | Chat | Sonnet |
| Quick code explanation / Q&A | Chat | Sonnet |
| Brainstorm architecture / flows | Chat | Sonnet |
| Long doc generation, synthesis, rewrites | Cowork | Sonnet |
| Multi-file summarising (handovers, snapshots) | Cowork | Sonnet |
| Build a thing, fix a bug, refactor | Claude Code (terminal) | Sonnet |
| Repo-wide audit / big refactor | Claude Code (terminal) | Opus |
| Complex debugging loop (30+ min) | Claude Code (terminal) | Opus |
| Technical design doc (full module) | Cowork | Opus |

**Rule:** Only switch to Opus when you'd take 30+ mins doing it yourself.

---

## 🚀 SESSION BOOT SEQUENCE (Every Single Time)

> Use this BEFORE you open ANY Claude window.

**Step 1 — 2-minute brain dump in Chat:**
```
Goal for this block: [one sentence]
Project: [HyperCode / Mission Control / Obsidian Brain / Course / SDK]
Output I need: [PR / markdown doc / bug fix / checklist]
What NOT to touch: [list any sacred files or running containers]
```

**Step 2 — Ask Claude to split:**
```
Split this into: 
1) Things Claude Code should do (file edits, git, tests)
2) Things Cowork should do (docs, synthesis, summaries)
3) Things only I can decide
Give me a numbered checklist. Max 5 items.
```

**Step 3 — Route and go.**
Open the right Claude window. Paste the relevant chunk. Build.

---

## 🏗️ PROJECT: HyperCode-V2.4

**Stack:** Docker (41 containers), FastAPI, Python, Prometheus, Grafana, Redis, PostgreSQL, Agent Swarm

### Claude Code — Boot Prompt
```
You are co-maintaining HyperCode-V2.4.
Stack: Docker Compose (docker-ce-cli ONLY, never docker.io), 
       FastAPI, Python 3.12, Redis DB1=cache DB2=rate-limits.
Sacred rules:
- from app.X import Y (NEVER from backend.app.X)
- 4 spaces indent, never 3, never mixed
- .env files NEVER committed
- git fetch before every push (auto-commits are running)

Read CLAUDE.md and WHATSDONE.md before suggesting anything.
Today's goal: [PASTE YOUR GOAL HERE]
Plan your approach in bullet points first. 
Show me diffs before committing anything.
```

### Cowork — Docs & Health Reports
```
I'm going to paste my latest ecosystem health data.
Generate a clean NEXT_SESSION_HANDOVER_[DATE].md with:
- What's healthy (one line each)
- What's broken + exact fix command
- Top 3 next tasks in priority order
- One-sentence starter for next session
Output: clean markdown, headers only, no waffle.
```

### Chat — Architecture / Planning
```
I'm building on HyperCode-V2.4. 
41 containers, 5 networks, FastAPI core on port 8000.
Current known issue: [DESCRIBE IT]
Give me 3 options to fix this. 
Start with the fastest safe option.
One option per bullet. No waffle.
```

---

## 🎮 PROJECT: Mission Control / WelshDog-Mission-Control

**Stack:** Express API, React panel, Discord integration, Catch Stragglers overlay

### Claude Code — Boot Prompt
```
You are working on WelshDog-Mission-Control.
Stack: Express API, React frontend.
Key facts:
- Catch Stragglers is LIVE (commits 00aa770, ceadad2, c5b36c2)
- CatchStragglers.jsx needs wiring into Mission Control main panel
- mcevents event-sourcing migration is TODO
- DISCORDBOTTOKEN goes in .env ONLY — never committed
- broski-bot: discord.py==2.4.0, entrypoint: python -u -m cogs.bot

Before touching anything: git fetch origin
Read WHATSDONE.md. Never rebuild what's listed there.
Today's task: [PASTE TASK]
Plan first. Show diffs. Commit only when I confirm.
```

### Cowork — Task Synthesis
```
I have a list of Mission Control tasks below.
Organise them into: 
  🔴 BLOCKER (stops launch)
  🟡 IMPORTANT (ship soon)  
  🟢 NICE TO HAVE (later)
For each blocker, write the exact command or file edit needed.
Keep it short. Bullets only.

TASKS: [PASTE YOUR LIST]
```

---

## 🧬 PROJECT: BROski-Obsidian-Brain

**Stack:** FastAPI on port 8100, 8 live modules, Container 30 (central spine), Obsidian vault

### Claude Code — Boot Prompt
```
You are working on BROski-Obsidian-Brain-for-HyperFocus-z0ne.
Stack: Python FastAPI on port 8100, 8 live modules.
Container 30 is the central spine — if it goes down, vault AI sync stops.
Current gaps (levels 18-20):
  - Level 18: AI Distraction Filter (wiring incomplete)
  - Level 19: DifficultyDial / Dynamic XP (not started)
  - Level 20: Brain-Constellation (blueprint exists, not live)

Check WHATSDONE.md before any suggestion.
Read CLAUDE.md for sacred rules.
Today's goal: [PASTE GOAL]
Plan in bullet points. Show diffs. No surprises.
```

### Chat — Brain Design
```
I'm designing a feature for my Obsidian Second Brain.
It's a FastAPI + Obsidian vault system with:
- PARA structure (Inbox, Projects, Areas, Resources, Archive)
- BROski$ coin economy (earn/spend via FastAPI)
- HyperSplit task decomp (ADHD-safe micro-chunks)

Feature I want: [DESCRIBE IT]
Give me: Why this helps neurodivergent workflows, 
         How it connects to existing modules, 
         One example API endpoint to start with.
```

---

## 📚 PROJECT: Hyper-Vibe-Coding-Course

**Stack:** Vite React, Vercel, Supabase, Stripe, BROski tokens (NOT Next.js — ever)

### Claude Code — Boot Prompt
```
You are working on Hyper-Vibe-Coding-Course.
Stack: Vite React (NOT Next.js App Router — never generate that).
       Vercel deploy, Supabase DB, Stripe payments, BROski tokens.
Sprint 4 anon signup is LIVE (commit a12ecd0, May 19).
Source of truth: rewrites/NEXT_SESSION_HANDOVER_latest.md

Sacred rules:
- npm run dev:frontend (NEVER npm run dev)
- Never supabase db push (use apply-migration only)
- WagmiRainbowKit stays in BROskiPets only, never global app root
- set-state-in-effect = hard lint fail, avoid entirely

Read WHATSDONE.md first. 
Today's task: [PASTE TASK]
```

### Cowork — Module Rewrites
```
I need to rewrite a course module following The HyperFocus Way structure:
1. STOP — plain English context, no jargon
2. WHY — real-world use case (Netflix/Stripe/Uber style)
3. HOW — numbered steps, one thought per step
4. WIN — explicit celebratable moment
5. NEXT — warm handoff to next module
6. HELP — troubleshooting section
7. REWARD — BROski XP claim prompt

Module to rewrite: [MODULE NAME + raw notes/transcript]
Audience: neurodivergent builders (ADHD, Dyslexia, Autistic)
Tone: friendly, casual, "mate-style". Celebrate wins. Short sentences first.
```

---

## 🤖 PROJECT: HyperAgent-SDK

**Stack:** TypeScript/npm, package: @w3lshdog/hyper-agent@0.1.7, manifest.json agent defs

### Claude Code — Boot Prompt
```
You are working on HyperAgent-SDK.
Package: @w3lshdog/hyper-agent — npm agent orchestration framework.
Stack: TypeScript, manifest.json for agent definitions, swarm coordination.

Check WHATSDONE.md before suggesting anything.
Do not rebuild what's listed there.
Today's goal: [PASTE GOAL]
Plan first. Show me the diff. I'll confirm before you commit.
```

---

## 💎 NO-WASTE RULES — Protect Your Pro Quota

### Never burn Opus on:
- Single-line bug fixes
- "What does this do?" questions
- Checking if a container is healthy (that's a terminal command)
- Explaining concepts you already know
- Anything under 10 minutes to do manually

### Always use Opus for:
- Repo-wide refactors (touching 5+ files)
- Debugging loops that are genuinely stuck
- Full module rewrites (course content)
- Complex architecture decisions
- Anything you'd book 30+ mins in a calendar for

### Kill the session politely when Claude drifts:
```
Stop. You're going off track.
My goal is: [ONE SENTENCE]
Give me only: [EXACT OUTPUT FORMAT]
```

---

## ⏱️ DAILY HYPERFOCUS WORKFLOW

### Morning Boot (15 min)
```
CHAT — Open Desktop > Chat
"Morning brain dump. Here's everything on my plate:
[LIST ALL PROJECTS + TASKS]
Sort these into: 
  ⚡ HYPERFOCUS NOW (1 thing)
  📋 TODAY (3 things)
  🗓️ THIS WEEK (everything else)
For the HYPERFOCUS NOW task — what's the first command or file edit?"
```

### Build Block (Pomodoro: 25 min on, 5 off)
- Open terminal → `cd [PROJECT_REPO]` → `claude`
- Paste Claude Code boot prompt for that project
- Let Claude plan first
- You approve → Claude builds
- After each chunk: `git add -A && git commit -m "..."` (Claude drafts message)

### Wrap + Handover (10 min)
```
COWORK — Open Desktop > Cowork
"Generate NEXT_SESSION_HANDOVER_[TODAY'S DATE].md
Based on what we did today:
[PASTE SUMMARY OF CHANGES]
Include: what's done, what's next, any blockers, first task for next session.
Push-ready markdown format."
```

---

## 🔥 POWER MOVES (Advanced)

### Multi-repo morning audit
```
CLAUDE CODE — run in HyperCode-V2.4 root:
"Scan all WHATSDONE.md files across repos. 
List anything marked TODO or IN PROGRESS.
Group by: 🔴 blocking launch / 🟡 important / 🟢 nice-to-have.
No commentary. Just the list."
```

### Grafana dashboard spec
```
COWORK:
"I have these metrics from my ecosystem health report: [PASTE METRICS]
Design a Grafana dashboard spec:
- Panel names
- Metric sources (Prometheus endpoint)
- Alert thresholds
Output as a clean markdown table."
```

### Auto-handover at end of every session
```
COWORK:
"Write NEXT_SESSION_HANDOVER_[DATE].md from this session summary:
[PASTE WHAT YOU DID]
Format: 
## ✅ Done
## 🔴 Blockers  
## ⚡ Next Task (1 sentence)
## 📝 Add to NotebookLM
"
```

---

## 🧱 SACRED RULES REMINDER (Never Break These in ANY Claude Session)

| Rule | Why |
|---|---|
| `docker-ce-cli` not `docker.io` | Agent socket connectivity |
| `from app.X import Y` | Import structure for FastAPI |
| `.env` files never committed | Security — always |
| Stripe webhook: `--no-verify-jwt` | Webhooks must be public |
| `4 spaces` Python indent | Never 3, never mixed |
| Redis DB1=cache, DB2=rate-limits | Never mix |
| `npm run dev:frontend` | NOT `npm run dev` |
| `discord.py==2.4.0` for broski-bot | Never py-cord |
| Bot entrypoint: `python -u -m cogs.bot` | Never `python main.py` |
| `git fetch` before push | Auto-commits are running |
| Nothing is done until it's pushed | Always commit to confirm |

---

> ⚡ Built by welshDog × Perplexity AI — June 2026
> Keep it weird, keep it Welsh. Stop apologising for your brain. Start building.
