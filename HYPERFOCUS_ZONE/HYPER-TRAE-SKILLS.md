# 🧠 Hyper Trae Skills — Master Reference
> Built by WelshDog | HYPERFOCUS z0ne | Trae IDE + SOLO Mastery  
> Last Updated: May 25, 2026  
> Pages Read: 13 TRAE SOLO docs  
> Status: 🟢 COMPLETE FIRST BUILD

---

## 📚 Pages Covered
1. [What is TRAE IDE](https://docs.trae.ai/ide/what-is-trae?_lang=en)
2. [What is TRAE SOLO](https://docs.trae.ai/solo/what-is-trae-solo?_lang=en)
3. [14 Must-Install Skills](https://docs.trae.ai/solo/14-must-install-skills-for-trae-solo?_lang=en)
4. [Automation](https://docs.trae.ai/solo/automation?_lang=en)
5. [GitHub Connector](https://docs.trae.ai/solo/github-integration?_lang=en)
6. [Worktree](https://docs.trae.ai/solo/worktree?_lang=en)
7. [Sandbox](https://docs.trae.ai/solo/sandbox?_lang=en)
8. [Skills](https://docs.trae.ai/solo/skills?_lang=en)
9. [Rules](https://docs.trae.ai/solo/rules?_lang=en)
10. [MCP Overview](https://docs.trae.ai/solo/mcp-overview?_lang=en)
11. [Workflow: Spec & Plan](https://docs.trae.ai/solo/spec-and-plan-as-different-workflows?_lang=en)
12. [Commands](https://docs.trae.ai/solo/slash-commands?_lang=en)
13. [Add MCP Servers](https://docs.trae.ai/solo/remote-mcp-server?_lang=en)

---

## 🔧 What is TRAE?

- **TRAE IDE** — AI-powered dev environment with two modes: classic IDE + SOLO
- **TRAE SOLO** — Standalone AI-native workspace (web, desktop, mobile)
- **MTC Mode** — More Than Coding — for non-devs (PMs, analysts, ops)
- **Code Mode** — For devs — agent-driven coding, debugging, Git workflows
- Cloud Agent runs tasks in isolated, stable per-session containers
- Privacy Mode — code stays local, never used for training

---

## 📦 14 Must-Install Skills

### 🛠️ Dev Tools
| Skill | What It Does |
|---|---|
| `git-commit` | Auto-generates conventional commit messages, stages & commits |
| `react-best-practices` | Code review + perf analysis for React/Next.js projects |
| `webapp-testing` | Playwright-based automated test scripts |
| `composition-patterns` | Refactors complex components + optimises state management |

### ⚡ Productivity
| Skill | What It Does |
|---|---|
| `agent-browser` | Scripted browser ops — page interaction, data extraction |
| `brainstorming` | Sorts & clarifies requirements → design plans + docs |

### 🎨 UI Design
| Skill | What It Does |
|---|---|
| `figma` | Parses Figma drafts → generates frontend code |
| `frontend-design` | Builds bold, styled UIs with layouts, colour, motion |
| `frontend-skill` | Builds clean, structured UIs with restrained visual style |

### 📊 Data Analysis
| Skill | What It Does |
|---|---|
| `chart-visualization` | Picks chart types + generates trend/comparison visuals |
| `data-analysis` | SQL queries on Excel/CSV → structured output |

### ✍️ Content Creation
| Skill | What It Does |
|---|---|
| `canvas-design` | Generates posters, covers, static visual content |
| `byted-seedream-image-generate` | AI image generation skill |
| `doc-coauthoring` | Phased collaborative doc writing (PRDs, reports, etc.) |

---

## ⚡ Automation
> Auto-execute tasks on a schedule — no manual input needed

### Use Cases for Hyper-Vibe
- 🔒 Daily security scan on all repos
- 📊 Weekly KPI report for HYPERFOCUS z0ne
- 🐾 BROskiPets changelog auto-generation
- 📰 Competitor/AI news aggregation feed

### Schedule Types
- Fixed time (daily/weekly/monthly)
- Recurring interval (every X mins/hours/days)
- Custom natural language → "9AM on workdays" (chat creation only)

### Create Flow
1. Sidebar → Automation
2. Pick: Chat / Manual / Template
3. Set runtime env + output storage
4. AI builds it → appears in Configured tab

> ⚠️ Mode + env + output location are LOCKED after creation — plan carefully!

---

## 🐙 GitHub Connector
> Code mode only — connect via Settings → Connectors → GitHub

### Key Powers
- Create PRs from inside TRAE (no browser switching!)
- AI auto-generates PR title + summary from diff
- AI reviews PRs with full git diff analysis
- Works on SOLO Web + Desktop

### Steps
1. Avatar → Settings → Connectors → Connect GitHub
2. Authorize TRAE-AI to your repos
3. Web: select repo in chat box | Desktop: open project → Cloud mode
4. Chat instructions → AI codes → AI Create PR → confirm → merge on GitHub

### Hyper-Vibe Use Cases
- 🔀 AI-create PRs for Hyper-Vibe-Coding-Course feature branches
- 🔍 AI review PRs before merging to main
- 🐾 BROskiPets smart contract PR review before deploy
- 🤖 BROski-Brain branch management

---

## 🌳 Worktree
> Parallel tasks, isolated Git environments — local env only, needs Git

### Key Powers
- Run feature dev + bug fix simultaneously with zero conflict
- AI auto-creates branch + directory per task
- AI Merge resolves conflicts automatically
- Keep branch even after cleaning local directory

### Steps
1. Bottom-left → switch mode to Worktree
2. Start task → agent creates branch automatically
3. Done → AI Merge or Manual Merge
4. Clean up via task list / Settings → Worktree

### Settings to Configure
- ✅ Default Keep Branch When Cleaning Worktree
- 🔔 Disk Space Usage Reminder threshold

### Hyper-Vibe Use Cases
- 🐾 BROskiPets: work on new NFT traits while fixing mint bug
- 🎓 Hyper-Vibe-Course: feature branch + hotfix in parallel
- 🤖 BROski-Brain: new agent module + existing agent fixes

---

## 🔐 Sandbox
> Isolated execution env — macOS Desktop (Code mode) + all Cloud/Web sessions

### Key Powers
- Intercepts high-risk commands (rm -rf etc) before they run
- Cloud sessions: fully isolated containers per session
- Local: macOS sandbox-exec, zero config needed
- Allowlist: trust specific command prefixes to bypass sandbox

### Enable
Avatar → Settings → Conversation → Auto-Run → "Sandbox with Allowlist"

### High-Risk Command Options
- **Skip** → don't run
- **Add to Allowlist** → always trust this prefix
- **Run** → execute in sandbox once

### File Access (Local)
- ✅ Read-write: project files, /tmp, cache, toolchains
- 🔒 Read-only: .vscode, root /
- 🚫 No access: host filesystem, other sessions

### Hyper-Vibe Use Cases
- 🔒 Safe smart contract deployment scripts
- 🛡️ Protect Supabase env vars from accidental agent overwrites
- ⚡ Let trusted npm/pip commands bypass sandbox via allowlist

---

## 🎯 Skills
> SKILL.md files — on-demand loaded professional capabilities for the agent

### Key Concept
- Agent scans brief descriptions first → only loads relevant skills
- Saves tokens + keeps context clean
- Skills vs Rules vs MCP:
  - **Skills** → loaded on-demand, HOW to do a task
  - **Rules** → always loaded, permanent behaviour constraints
  - **MCP** → provide tools the agent can call

### File Structure
```
skill-name/
├── SKILL.md          # Required — name + description in YAML front matter
├── examples/         # Optional — input/output demos
├── templates/        # Optional — reusable templates
└── resources/        # Optional — scripts, style guides
```

### SKILL.md Format
```yaml
---
name: skill name
description: what it does and when to use it
---
## Description
## When to use
## Instructions
## Examples
```

### Skill Locations
- Project skill: `.trae/skills/` (project only)
- Global skill: `~/.trae/skills/` (all projects)

### Call Methods
- Type `/` in chat → pick skill
- Tell AI: "Use the X skill to do Y"
- Auto-called when AI detects relevance

### Hyper-Vibe Custom Skills to Build 🔥
- `hyper-vibe-pr-review` → AI PR review to WelshDog standards
- `broSkipets-deploy` → smart contract deploy checklist
- `stripe-integration` → payment flow test SOP
- `supabase-migration` → DB migration safety steps
- `module-rewrite` → STOP/WHY/HOW/WIN/NEXT format enforcement

---

## 📋 Rules
> Always-on AI behaviour constraints — injected into every chat

### Rule Files
- `AGENTS.md` → project-level, root dir, cross-IDE compatible
- `CLAUDE.md` → auto-imported from Claude Code projects ✅
- Global Rules → Avatar → Settings → Rules

### Best Practices
- One rule = one concern (no overlap)
- Use relative file paths
- After editing rules → start a fresh chat
- Legacy code conflict → explicitly say "this is a refactor"

### Hyper-Vibe Rules to Write
- "Always use TypeScript strict mode"
- "All Python functions need docstrings"
- "Solidity contracts must include NatSpec comments"
- "Never expose env vars in responses"
- "Always follow STOP/WHY/HOW/WIN/NEXT structure for module content"

---

## 🔌 MCP (Model Context Protocol)
> Connects TRAE agents to external tools & services

### Transport Types
| Type | Transport | Runs Where |
|---|---|---|
| `stdio` | stdin/stdout | Local only |
| `HTTP` | SSE | Local or Remote |
| `Streamable HTTP` | Streamable HTTP | Local or Remote |

### MCP Scope
| Type | Applies To | Client |
|---|---|---|
| **Global MCP** | All projects + tasks | Web + Desktop |
| **Project MCP** | Current project only | Desktop (local tasks only) |

### Runtime
- Local → local tasks, Desktop only
- Cloud → GitHub projects, Web + Desktop

### Hyper-Vibe MCP Ideas 🔥
- `@modelcontextprotocol/server-github` → deep GitHub control
- Supabase MCP → direct DB queries from agent
- Stripe MCP → payment event triggers
- Pinata/IPFS MCP → NFT asset management
- Discord MCP → BROski bot integration

> ⚠️ Third-party servers — check regional availability + security before adding

---

## 🔌 Add MCP Servers

### From Marketplace
1. Avatar → Settings → MCP
2. (Desktop) Pick Local or Cloud
3. Create → Create from Market
4. Browse → click + → fill config (replace API keys)
5. Confirm

### Manual Config
1. Avatar → Settings → MCP
2. (Desktop) Pick Local or Cloud
3. Create → Create Manually
4. Paste JSON config
5. Confirm

> 💡 Prefer NPX or UVX — no global install needed, auto-handles dependencies

### stdio MCP Config
```json
{
  "mcpServers": {
    "github-mcp": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "ghp_xxxxx"
      }
    }
  }
}
```

### HTTP MCP Config
```json
{
  "mcpServers": {
    "supabase-mcp": {
      "url": "https://your-mcp-server.com/mcp",
      "headers": {
        "Authorization": "Bearer xxxx"
      }
    }
  }
}
```

### Timeout Settings
- `START_MCP_TIMEOUT_MS` → startup timeout (ms)
- `RUN_MCP_TIMEOUT_MS` → tool call timeout (ms)

### Project-Level MCP (Desktop Local only)
- Create `.trae/mcp.json` in project root
- Enable: Settings → MCP → Local → Enable Project MCP
- Use `${workspaceFolder}` variable for paths

---

## 📋 Workflow: Spec & Plan
> Two planning modes — Spec for complex, Plan for medium tasks

### 🏗️ Spec Workflow
**When:** System-level tasks, large refactors, multi-person projects, critical systems (payment, security)

**Output:** 3 docs in `.trae/specs/`
- `spec.md` → full outline of system/feature
- `tasks.md` → task breakdown
- `checklist.md` → acceptance criteria per phase

**Flow:**
1. AI generates 3 docs → **pauses for your approval**
2. Edit manually OR tell AI what to change
3. Confirm → AI executes + auto-updates task/checklist status

**Enable:** `/spec` or `/` → Spec

### 🚀 Plan Workflow
**When:** Small-to-medium features, module-level refactoring

**Output:** `plan.md` in `.trae/documents/`

**Flow:**
1. AI analyzes requirements → generates plan
2. You confirm or request changes
3. AI executes tasks one by one

**Enable:** `/plan` or `/` → Plan

### Hyper-Vibe Use Cases
- 🏗️ **Spec:** BROskiPets v2 architecture redesign
- 🏗️ **Spec:** Hyper-Vibe-Course full payment + auth flow
- 🏗️ **Spec:** Mission Control dashboard rebuild
- 🚀 **Plan:** Add new lesson module to course
- 🚀 **Plan:** BROskiPets new trait generator
- 🚀 **Plan:** Add Catch Stragglers to Mission Control panel

---

## ⚡ Commands
> Slash commands — reusable shortcuts for repetitive tasks

### Built-In Commands
| Command | What It Does |
|---|---|
| `/plan` | Invoke Plan workflow |
| `/spec` | Invoke Spec workflow |
| `/browser_use` | Use built-in browser tool for validation |

### Create a Custom Command
1. Avatar → Settings → Skills & Commands
2. (Desktop) Pick Local or Cloud runtime
3. Click Create
4. Fill in: Command Name, Description, Instructions
5. Confirm

> Command Name rules: lowercase letters, numbers, hyphens only
> Example: `summarize-pr-info`

### Use a Command
1. Type `/` in chat OR click command icon
2. Select from menu
3. Add context + send

### Hyper-Vibe Custom Commands to Build 🔥
- `/hyper-pr-review` → Code review to WelshDog standards
- `/broSkipets-deploy-check` → Pre-deploy smart contract checklist
- `/stripe-test-flow` → Automated payment flow validation
- `/supabase-migration-safe` → DB migration safety check
- `/commit-msg` → Generate Conventional Commits message
- `/module-audit` → Check module follows STOP/WHY/HOW/WIN/NEXT

---

## 🔑 Power Features Quick Ref

| Feature | What It Does | Enable |
|---|---|---|
| **CUE** | Smart code completion + next-edit prediction (Python, TS, Go) | Auto |
| **Agent** | Natural language → multi-step execution | Default |
| **Context** | Feed files, URLs, repos, terminal output | `@` in chat |
| **Sandbox** | Intercepts dangerous commands | Settings → Conversation |
| **Privacy Mode** | Code stays local, not used for training | Settings → Privacy |
| **Voice Input** | Mobile voice dispatch to desktop agents | Mobile app |
| **Worktree** | Parallel tasks, isolated Git environments | Bottom-left mode switch |
| **Automation** | Scheduled tasks, zero manual input | Sidebar → Automation |

---

## 🗺️ Hyper-Vibe TRAE Setup Checklist

### Connect First
- [ ] Connect GitHub → Settings → Connectors
- [ ] Add GitHub MCP server (stdio)
- [ ] Add Supabase MCP server
- [ ] Enable Sandbox with Allowlist
- [ ] Enable Project MCP for each repo

### Install Skills (Marketplace)
- [ ] `git-commit`
- [ ] `react-best-practices`
- [ ] `webapp-testing`
- [ ] `brainstorming`
- [ ] `doc-coauthoring`
- [ ] `frontend-design`

### Build Custom Skills
- [ ] `hyper-vibe-pr-review`
- [ ] `broSkipets-deploy`
- [ ] `supabase-migration`
- [ ] `module-rewrite`

### Build Custom Commands
- [ ] `/hyper-pr-review`
- [ ] `/commit-msg`
- [ ] `/supabase-migration-safe`
- [ ] `/module-audit`

### Set Up Rules
- [ ] Create `AGENTS.md` in each repo root
- [ ] TypeScript strict mode rule
- [ ] Python docstring rule
- [ ] Env var protection rule

---

## 📖 Still To Explore
- [ ] Cloud Environments deep-dive
- [ ] Models — which AI model + when to pick each
- [ ] Voice Discussion
- [ ] Privacy Mode detailed settings
- [ ] Lark / Feishu Connector
- [ ] Chat Settings

---

> 🔄 Keep adding as we explore more TRAE docs!
> Built with ❤️‍🔥♾️ by WelshDog + Perplexity — HYPERFOCUS z0ne
