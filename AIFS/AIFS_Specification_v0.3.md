# AIFS — AI File System Specification v0.3

> **The Folder Contract Protocol for AI Agents**

Built by welshDog × Perplexity | June 2026

---

## 1. Core Principle

Every folder that AI touches must declare its own rules. The AI reads the nearest contract first, obeys local rules before global ones, and stops if the folder says "hands off."

The folder is the boundary. The contract is the law. The AI obeys before it edits.

---

## 2. The Contract Stack

### Primary Layer (Three Files)

| File | Purpose | Audience | Format |
|------|---------|----------|--------|
| `AGENTS.md` | Behavior, safety, guardrails | AI agents | Markdown |
| `folder.prompt.md` | Plain-English intent | Humans + AI | Markdown |
| `manifest.toml` | Machine-readable policy | AI + CI/CD | TOML |

### Power-Up Layer (Optional)

| File | Purpose |
|------|---------|
| `.ailock` | Hard stop — like `.gitignore` but for AI. Lines = files/patterns the AI must never touch. |
| `context.md` | Live state — current task, last AI edit, known in-flight work. |
| `TRUST.md` | Per-agent trust tiers — FULL / EDIT_ONLY / READ_ONLY / BLOCKED. |
| `ttl.toml` | Time-expiring rules — `read_only_until = "2026-07-01"`. Auto-drops after date. |

---

## 3. Discovery Order

1. AI enters a folder
2. Checks `.ailock` → if matched, **FULL STOP**
3. Loads `AGENTS.md` → behavior and safety rules
4. Loads `manifest.toml` → strict machine policy
5. Loads `folder.prompt.md` → intent and context
6. Loads `context.md` → live sprint state
7. Loads `TRUST.md` → agent trust tier for calling agent
8. If none exist → inherit from parent folder
9. If root has none → use global tool defaults

---

## 4. Resolution Rules

| Rule | Behaviour |
|------|-----------|
| `MUST NOT` vs `MAY` | `MUST NOT` wins. Deny-by-default. |
| `read_only = true` | Blocks ALL write actions, overrides everything. |
| `.ailock` match | Immediate hard stop. No exceptions. |
| Local vs Parent | Local wins. Parent inherits if `inherit = true`. |
| Subfolder relaxation | Blocked unless parent `relaxation_allowed = true`. |
| Agent trust tier | READ_ONLY agents cannot write even if `manifest.toml` allows it. |
| When unclear | STOP & ASK. Never guess. |

### 4.1 Precedence Order (Highest → Lowest)

1. **User instruction** (explicit human override)
2. **`.ailock`** (hard stop patterns)
3. **Agent trust tier** from `TRUST.md`
4. **Nearest `AGENTS.md`** (local behavior)
5. **Nearest `manifest.toml`** (local policy)
6. **`context.md`** (in-flight work protection)
7. **Parent `AGENTS.md`** (inherited behavior)
8. **Parent `manifest.toml`** (inherited policy)
9. **Global defaults** (tool fallback)

---

## 5. File Specs

### 5.1 AGENTS.md

```markdown
# AGENTS.md — /[folder-name]

## Identity
[What this folder is — one sentence]

## Permissions
- MAY: Create `.md` files.
- MAY: Edit `.md` and `.txt` files.
- MUST NOT: Delete files.
- MUST NOT: Rename files without approval.
- MUST NOT: Edit files outside this folder.

## Output Format
- New files: [format]
- Code: [language with explicit types]

## Safety
- Read-only: false
- Require approval for: delete, rename, move
- Summarize planned changes before editing.

## Overrides
- Subfolders may define stricter rules.
- Subfolders may NOT relax these rules.
```

**Required sections:** `Identity`, `Permissions`, `Output Format`, `Safety`
**Optional sections:** `Overrides`, `Examples`, `References`

---

### 5.2 manifest.toml

```toml
[contract]
version = "0.3"
folder = "/docs"
read_only = false
inherit = true

[permissions]
create = [".md"]
edit = [".md", ".txt"]
delete = false
rename = "approval"   # "true" | "false" | "approval"
move = "approval"

[output]
default_format = "markdown"
frontmatter = true
code_language = "typescript"

[safety]
require_approval_for = ["delete", "rename", "move"]
max_file_size_kb = 500
allowed_external_refs = false

[subfolders]
override_allowed = true
relaxation_allowed = false

# Optional: approval routing
[approval]
channel = "discord"           # "discord" | "vscode" | "console"
webhook_env = "DISCORD_WEBHOOK_AIFS"
timeout_seconds = 30
timeout_action = "deny"       # "deny" | "allow"
```

---

### 5.3 .ailock

Like `.gitignore` — one pattern per line. Matched files = AI hard stop.

```
# .ailock
migrations/*.sql
secrets/**
legacy/**
*.env
NEVER_EDIT_THIS.md
```

---

### 5.4 context.md

Live sprint state. AI reads this BEFORE touching anything.

```markdown
# context.md

## Active Task
Sprint 4 — anonymous → signup flow.

## Last AI Edit
2026-06-02 — added ClaimXPModal.tsx

## In-Flight (Do Not Touch)
- `lib/migrateAnonProgress.ts` — active rewrite, do not modify
- `hooks/useAnonymousProgress.ts` — under test

## Approved to Edit
- `components/ClaimXPModal.tsx`
- `app/vibe-labs/**/*.tsx`
```

---

### 5.5 TRUST.md

Per-agent trust tiers. Unknown agents default to READ_ONLY.

```markdown
# TRUST.md

## Trust Levels
- claude-3.5-sonnet: FULL
- github-copilot: EDIT_ONLY
- cursor: EDIT_ONLY
- unknown: READ_ONLY

## Trust Definitions
- FULL: All permissions per manifest.toml
- EDIT_ONLY: May edit existing files, may NOT create or delete
- READ_ONLY: May read only, zero writes
- BLOCKED: No access at all
```

---

### 5.6 ttl.toml

Rules that auto-expire. After the date passes, rule drops to default.

```toml
[rules]
read_only = true
read_only_until = "2026-07-01"
reason = "Migration in progress — do not edit until complete"

[rules.after_expiry]
read_only = false
```

---

## 6. Inheritance & Override Rules

```
/root
├── AGENTS.md          (global: no deletes anywhere)
├── manifest.toml      (global: default_format = markdown)
├── /docs
│   ├── AGENTS.md      (local: may create .md)
│   ├── folder.prompt.md
│   ├── manifest.toml  (local: read_only = false)
│   └── /api
│       └── manifest.toml  (inherits /docs, overrides output format)
└── /migrations
    └── .ailock        (FULL STOP — nothing edits here)
```

| Scenario | Behaviour |
|----------|-----------|
| No local contract | Inherit from nearest parent with a contract. |
| Local `AGENTS.md` exists | Merge with parent. Local rules override parent rules. |
| `manifest.toml` says `inherit = false` | Ignore all parent contracts. Use only local rules. |
| Subfolder tries to relax a rule | Blocked if parent `relaxation_allowed = false`. |
| `MUST NOT` vs `MAY` | `MUST NOT` wins. |
| `.ailock` match | Hard stop. |
| TTL rule expired | Drop to default. Validator warns if expired rule found. |

---

## 7. Special Folders

| Folder | Implicit Rule |
|--------|--------------|
| `.ai/` | Read-only by default. AI may read, must not edit unless explicit. |
| `.templates/` | Copy-only. AI may copy from, must not edit in place. |
| `.archive/` | Read-only. No edits without explicit override. |
| `.contracts/` | Reserved. Inherits root rules only. |
| `migrations/` | Recommend `.ailock` — SQL migrations are dangerous. |
| `node_modules/`, `.git/`, `__pycache__/` | Ignored by all AI agents. |

---

## 8. Cross-Tool Compatibility

| Tool | Native File | AIFS Equivalent |
|------|------------|----------------|
| Claude Code | `CLAUDE.md` | `AGENTS.md` |
| Cursor | `.cursorrules` / `.mdc` | `AGENTS.md` + `manifest.toml` |
| GitHub Copilot | `.github/copilot-instructions.md` | `AGENTS.md` |
| Windsurf | `.windsurfrules` | `AGENTS.md` |
| Cline | `.clinerules` | `AGENTS.md` |
| OpenAI Codex | `AGENTS.md` | Native |
| Gemini CLI | `GEMINI.md` | `AGENTS.md` |
| Aider | `.aider.conf.yml` | `manifest.toml` + `AGENTS.md` |
| MCP Servers | `mcp.json` | `manifest.toml` |

```bash
# Export AIFS contracts to tool-specific files
aifs export --tool=cursor --out=./.cursor/rules/
aifs export --tool=copilot --out=./.github/instructions/
aifs export --tool=claude --out=./CLAUDE.md
```

---

## 9. The Watcher Daemon

`aifs_watcher.py` is a real-time enforcement daemon — not just a CI check.

```
AI edits file
    → watcher intercepts
    → resolves nearest manifest.toml
    → checks .ailock patterns
    → checks TRUST.md for agent
    → ALLOW / BLOCK / QUEUE FOR APPROVAL
    → logs to CHANGELOG.ai.md
    → Discord ping if approval needed
```

Run it:
```bash
python AIFS/aifs_watcher.py watch . --discord-webhook=$DISCORD_WEBHOOK_AIFS
```

---

## 10. Roadmap

| Phase | Status |
|-------|---------|
| v0.1 — Core spec | ✅ Done |
| v0.2 — Validator + CI | ✅ Done |
| v0.3 — Watcher + TTL + TRUST + .ailock | ✅ Done |
| v0.4 — MCP resource integration | 🔜 Next |
| v0.5 — AIFS Hub dashboard | 🔜 Future |
| v0.6 — Cryptographic contract signing | 🔜 Future |
| v1.0 — AIFS Registry (shareable contracts) | 🔜 Future |

---

## 11. Future-Proofing

- **Schema versioning** — `manifest.toml` declares spec version
- **`x_` extensions** — custom sections prefixed `x_` are allowed, ignored by standard validators
- **MCP integration** — contracts discoverable as MCP resources
- **WSP alignment** — `skills.txt` / `agents.txt` can reference AIFS contracts
- **Cryptographic signing** — reserved v0.6
- **Audit logging** — `CHANGELOG.ai.md` append-only per folder

---

*End of Specification v0.3*

*Built by welshDog × Perplexity — Llanelli, Wales 🏴󠁧󠁢󠁷󠁬󠁳󠁧 — June 2026*
