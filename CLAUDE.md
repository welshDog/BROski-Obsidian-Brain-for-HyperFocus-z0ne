# 🧠 CLAUDE.md — THE HYPER BRAIN v3.0
> Read this FIRST. Every session. No exceptions.
> Builder: @welshDog — Lyndz Williams, S.Wales 🏴󠁧󠁢󠁷󠁬󠁳󠁠
> Neurodivergent-first Second Brain — ADHD + Dyslexia + Autistic.

---

## 👤 Who You're Working With
- **Name:** Lyndz — call them "Bro" or "BROski"
- **Profile:** ADHD + Dyslexia + Autistic
- **Style:** Short bullets. Bold keys. Emojis. Why → How → Example. NEVER walls of text.
- **Energy:** Celebrate wins. Quick wins FIRST. Momentum > perfection.
- **Sacred Rule:** NEVER debate these rules. NEVER suggest removing them.

---

## 🏗️ This Repo — What It Is

**THE HYPER BRAIN v3.0** — Obsidian Second Brain for the HyperFocus Zone ecosystem.

- Vault lives at: `HYPERFOCUS_ZONE/` (open THIS folder as Obsidian vault)
- Vault is the repo root on local: `H:\BROski-Obsidian-Brain-for-HyperFocus-z0ne`
- Auto-commits every 10 mins via Obsidian Git plugin
- GitHub sync script: `scripts/github_to_obsidian.py`
- Brain API container: `hyper_brain_core.py` → port 8100

---

## 🌐 The Ecosystem (4 linked repos)

| Repo | What | Port/Path |
|------|------|-----------|
| **HyperCode-V2.4** | Main platform — Docker, FastAPI, 32 containers | `localhost:8000` |
| **HyperAgent-SDK** | TypeScript SDK — agent spec, CLI | `localhost:4040` |
| **Hyper-Vibe-Coding-Course** | Course frontend — Supabase + Stripe | `localhost:5174` |
| **BROskiPets-LLM-dNFT** | AI pet NFTs — LLM + on-chain XP | `localhost:8098` |
| **THIS REPO** | Second Brain — Obsidian vault + AI layer | `localhost:8100` |

---

## 🗂️ Vault Structure (PARA + extensions)

```
HYPERFOCUS_ZONE/
├── 00-Inbox/              # Brain dump + GitHub issues + AI captures
│   ├── GitHub/            # Auto-synced: issues + PRs (webhook real-time)
│   ├── Discord/           # Community captures (future)
│   └── AI-Capture/        # Voice → Whisper → atomic notes (future)
├── 01-Projects/           # Active builds — 4 repos pre-seeded
├── 02-Areas/              # Health, Admin, DevOps, Focus-Analytics
├── 03-Resources/          # Economy table, snippets, Agent YAMLs, MCP configs
├── 04-Archive/            # Completed wins
├── 05-Focus-Sessions/     # Session logs with YAML frontmatter (Level 16)
├── 06-AI-Context/         # RAG chunks, prompt library (Level 20)
├── 07-Streaks-Achievements/ # Dynamic XP, streak recovery, badges (Level 19)
├── 99-Templates/          # Daily, Project, Task, Morning Briefing, Focus-Session
└── Hub/                   # Dashboard + Focus Command Center + Brain Constellation
```

**SACRED RULE:** Notes ALWAYS go in correct folder. NEVER dump in repo root.

---

## 🎮 Level Tracker

```
✅ Level 1–8   Vault scaffold + plugins + PARA structure
✅ Level 9    GitHub bridge LIVE (4hr polling)
✅ Level 10   Vault immortal (Obsidian Git auto-commit)
✅ Level 11   BROski$ Coin Tracker (Dataview widget)
✅ Level 12   Hyperfocus CSS Modes (Focus/Calm/Hyper)
⏳ Level 13   Morning Briefing AI (morning_briefing_ai.py + LLM)
⏳ Level 14   GitHub Webhooks real-time (github_webhook_server.py)
⏳ Level 15   HyperAgent AI Daily Briefing (mcp_bridge.py)
⏳ Level 16   Focus Tracker + Analytics (focus_tracker.py)
⏳ Level 17   HyperSplit Task Decomposition (hyper_split.py)
⏳ Level 18   AI Distraction Filter (ai_distraction_filter.py)
⏳ Level 19   DifficultyDial + Dynamic Gamification
⏳ Level 20   THE HYPER BRAIN Constellation (full MCP mesh + RAG)
```

---

## 🐈 Claude Hyper Skills — What You CAN Do Here

### 🥇 Tier 1 — Do These Automatically

1. **Note Writer + Filer**
   - Create notes in CORRECT vault folder always
   - Daily notes → `00-Inbox/` (never repo root)
   - Project notes → `01-Projects/`
   - Resources/snippets → `03-Resources/`
   - NEVER create files in repo root unless it's a README/CLAUDE/config

2. **Dataview Query Builder**
   - Write Dataview + DataviewJS queries for Dashboard
   - Knows BROski$ schema: `coins`, `xp`, `status`, `project` frontmatter keys
   - Always `SORT file.mtime DESC` and include `LIMIT` for performance

3. **Template Builder**
   - All templates use Templater syntax: `<% tp.date.now("YYYY-MM-DD") %>`
   - YAML frontmatter always includes: `created`, `tags`, `status`
   - Task templates always include: `coins`, `xp` fields

4. **Script Fixer + Enhancer**
   - All Python in `scripts/` or root `.py` files
   - Always use `os.environ.get()` with fallback for env vars
   - Never hardcode paths — use `OBSIDIAN_VAULT_PATH` env var
   - Docker: 4 spaces, absolute imports, mem_limit: 256m for hyper-brain

5. **CLAUDE.md + WHATS_DONE Updater**
   - After every significant change: update this file + WHATS_DONE section
   - Add to level tracker when level unlocked
   - Keep KEY FACTS section accurate

### 🥈 Tier 2 — On Request

6. **Vault Cleaner**
   - Detect + move misplaced files
   - Delete confirmed duplicates
   - Enforce PARA structure

7. **GitHub Issues → Task Notes**
   - Convert raw issue JSON → BROski Task template
   - Auto-assign coins/XP based on issue labels
   - File in correct `01-Projects/[repo]/` subfolder

8. **Focus Analytics Reporter**
   - Read `05-Focus-Sessions/` data
   - Generate weekly markdown report
   - Output to `02-Areas/Focus-Analytics/`

9. **Morning Briefing Generator**
   - Pull: GitHub open issues + HyperCode health + BROski$ balance + today's tasks
   - Write to `00-Inbox/Morning-[date].md`
   - Wire to `morning_briefing_ai.py` for LLM enhancement

### 🥉 Tier 3 — Advanced

10. **MCP Bridge Wiring (Level 15)**
    - `mcp_bridge.py` connects vault as MCP source
    - Every note = queryable context for HyperAgent
    - Config in `03-Resources/MCP/`

11. **Webhook Server (Level 14)**
    - `github_webhook_server.py` → FastAPI on port 8100
    - PR/issue events → instant vault note
    - HMAC-SHA256 validation always

12. **HyperSplit Wiring (Level 17)**
    - `hyper_split.py` → break any task into micro-steps
    - Output as `Task-HyperSplit.md` template
    - Recursive: each micro-task gets coins/XP

---

## 🔑 Key Facts (Never re-look-up)

```
Vault open path:     HYPERFOCUS_ZONE/
Local repo path:     H:\BROski-Obsidian-Brain-for-HyperFocus-z0ne
Brain API:           http://localhost:8100
GitHub sync script:  scripts/github_to_obsidian.py (needs GITHUB_PAT env var)
Token format:        github_pat_xxx (fine-grained, not ghp_)
Obsidian Git:        auto-commits every 10 mins, auto-push ON
CSS snippets:        HYPERFOCUS_ZONE/.obsidian/snippets/focus-mode.css
Focus mode classes:  body.focus-mode | body.calm-mode | body.hyper-mode
BROski$ schema:      coins (int), xp (int), status (todo/done), project (str)
Dataview plugin:     REQUIRED — all Dashboard queries depend on it
Templater plugin:    REQUIRED — all templates use tp.* syntax
HyperCode health:    http://localhost:8000/health
BROskiPets health:   http://localhost:8098/health
Docker context:      desktop-linux on Windows
Python style:        4 spaces, absolute imports, type hints preferred
Memory cap:          hyper-brain container = 256m MAX
Security:            NEVER commit .env / secrets / tokens
Frontmatter must:    created, tags, status (minimum on every note)
```

---

## 🚫 What NEVER To Do

- ❌ NEVER create files in repo root (except README/CLAUDE/configs)
- ❌ NEVER hardcode paths or tokens in scripts
- ❌ NEVER commit `.env` or any file containing `GITHUB_PAT`
- ❌ NEVER suggest ghost Obsidian plugins (always verify they exist)
- ❌ NEVER wall of text — always chunk + bullet
- ❌ NEVER skip updating WHATS_DONE after shipping something
- ❌ NEVER debate the Sacred Rules

---

## 🚀 Current Sprint — Level 13 Next

**Goal:** Wire `morning_briefing_ai.py` → LLM → daily vault note

**Steps:**
1. Check `morning_briefing_ai.py` — confirm API endpoints it calls
2. Ensure HyperCode `/health` + GitHub API + BROski$ endpoint wired
3. Test: `python morning_briefing_ai.py` → creates `00-Inbox/Morning-YYYY-MM-DD.md`
4. Docker: add to `hyper-brain` container startup
5. Verify in Obsidian: briefing appears in Inbox ✅

**LEVEL 13 UNLOCK = Morning Briefing drops into vault automatically every morning.**

---

> *"The brain that changes itself is the brain that builds itself."*
> **THE HYPER BRAIN v3.0 — BROski♾️ builds the future.**
