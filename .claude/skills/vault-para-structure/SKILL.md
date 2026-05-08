---
name: vault-para-structure
description: HYPERFOCUS_ZONE Obsidian vault PARA structure (00-Inbox..99-Templates). Where every note belongs, never dump in repo root, the sacred placement rule. Use when the user says "where does this go", "file this note", "organize", "PARA", "vault structure", "create a note", or asks about vault hygiene.
---

# vault-para-structure

The vault uses **PARA** (Projects, Areas, Resources, Archive) + extensions. Every note has exactly one correct folder. **Notes NEVER go in repo root.**

## The Vault Tree

```
HYPERFOCUS_ZONE/                ← OPEN THIS in Obsidian (NOT the repo root)
├── 00-Inbox/                   # New stuff, captures, AI drops
│   ├── GitHub/                 #   Auto-synced GitHub issues + PRs
│   │   ├── HyperCode-V2.4/
│   │   ├── HyperAgent-SDK/
│   │   ├── Hyper-Vibe-Coding-Course/
│   │   └── BROskiPets-LLM-dNFT/
│   ├── Briefings/              #   morning_briefing_ai.py output
│   └── AI-Capture/             #   Voice → Whisper → notes (future)
├── 01-Projects/                # Active builds — 4 repo subfolders
│   ├── HyperCode-V2.4/
│   ├── HyperAgent-SDK/
│   ├── Hyper-Vibe-Coding-Course/
│   └── BROskiPets-LLM-dNFT/
├── 02-Areas/                   # Ongoing responsibilities
│   ├── Health/
│   ├── Admin/
│   ├── DevOps/
│   └── Focus-Analytics/        #   Weekly reports from analytics_engine.py
├── 03-Resources/               # Reference material
│   ├── Economy/                #   BROski$ ledger snapshots
│   ├── Snippets/               #   Reusable code blocks
│   ├── Agent-YAMLs/            #   HyperAgent manifests
│   └── MCP/                    #   MCP config templates
├── 04-Archive/                 # Done + retired
├── 05-Focus-Sessions/          # focus_tracker.py output (one note per session)
├── 06-AI-Context/              # RAG chunks, prompt library
├── 07-Streaks-Achievements/    # XP, streak recovery, badges
├── 99-Templates/               # Daily, Project, Task, Briefing, Session
└── Hub/                        # Dashboard + Focus Command Center
```

## The Sacred Placement Rule

**Every note must land in the correct folder. Never dump in repo root or vault root.**

| Note type | Lives in |
|---|---|
| New idea / capture | `00-Inbox/` |
| GitHub issue/PR | `00-Inbox/GitHub/<repo>/` (auto-synced) |
| Daily briefing | `00-Inbox/Briefings/<date>.md` (auto-generated) |
| Active project doc | `01-Projects/<project-name>/` |
| Health log, admin task | `02-Areas/<area>/` |
| Code snippet, reference | `03-Resources/<topic>/` |
| Completed project | `04-Archive/<project>/` |
| Focus session log | `05-Focus-Sessions/<date-time>.md` (auto-generated) |
| LLM context chunk | `06-AI-Context/<topic>/` |
| XP / achievement | `07-Streaks-Achievements/` |
| Reusable template | `99-Templates/` |
| Dashboard widget | `Hub/Dashboard.md` |

## Frontmatter Standard

Every note has YAML frontmatter:

```yaml
---
created: 2026-05-08
tags: [project, hypercode, sprint-10n]
status: active                # active | parked | done | archived
project: HyperCode-V2.4       # if applicable
priority: high                # low | medium | high
---

# Note title

Content...
```

`focus_tracker.py` and `morning_briefing_ai.py` write frontmatter automatically. Manual notes should follow the same pattern.

## Templates (in `99-Templates/`)

| Template | Used for |
|---|---|
| `Daily.md` | Daily journal (one per day) |
| `Project.md` | New project kickoff |
| `Task.md` | Standalone task |
| `Morning-Briefing.md` | (Used by `morning_briefing_ai.py`) |
| `Focus-Session.md` | (Used by `focus_tracker.py`) |
| `BROski-Task.md` | Task with BROski$ XP/coin metadata |

Use Templater to instantiate: `Cmd+P → Templater: Insert Template`.

## Common Mistakes (and corrections)

| Wrong | Right |
|---|---|
| Note dumped in vault root | Move to `00-Inbox/` first, file to correct folder later |
| Project doc in `02-Areas/` | Active = `01-Projects/`. Areas = ongoing responsibilities (no end date) |
| Code snippet in `01-Projects/` | Move to `03-Resources/Snippets/` |
| Completed project still in `01-Projects/` | Move to `04-Archive/<project>/` |
| Random notes in repo root (outside `HYPERFOCUS_ZONE/`) | Move into the vault, file properly |
| Daily journal at vault root | Move to `00-Inbox/` (or use Daily Notes plugin to auto-place) |

## Vault Cleanup (when things drift)

```powershell
cd H:\BROski-Obsidian-Brain-for-HyperFocus-z0ne

# Find misplaced .md files at vault root (should be 0)
Get-ChildItem HYPERFOCUS_ZONE\*.md | Where-Object { $_.PSIsContainer -eq $false }

# Find empty folders (potential drift indicators)
Get-ChildItem HYPERFOCUS_ZONE -Directory -Recurse | Where-Object { @(Get-ChildItem $_.FullName).Count -eq 0 }
```

## Adding A New Folder

Only when it's a clear new category. Don't proliferate folders for one-off notes.

```powershell
# Example: new area
New-Item -ItemType Directory -Path "HYPERFOCUS_ZONE/02-Areas/Finance"
```

Then update this skill's tree.

## Companion Skills

- `obsidian-git-vault` — auto-commit ensures placement decisions persist
- `hyper-brain-modules` — modules write to specific PARA folders
- `morning-briefing-ai` — drops into `00-Inbox/Briefings/`

## Hard Rules

- **NEVER place notes in repo root** — always inside `HYPERFOCUS_ZONE/`
- **NEVER place notes in vault root** — always in a numbered folder
- **`HYPERFOCUS_ZONE/` is the Obsidian vault path** — open this in Obsidian, not the repo root
- **Active projects = `01-`. Ongoing areas = `02-`.** Don't confuse them
- **Completed projects move to `04-Archive/`** — don't leave them rotting in `01-Projects/`
