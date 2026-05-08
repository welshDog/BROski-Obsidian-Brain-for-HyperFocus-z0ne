---
name: obsidian-git-vault
description: HYPERFOCUS_ZONE vault auto-commit + auto-push via Obsidian Git plugin (Level 10 — Vault Immortal). 10-minute commit cycle, conflict resolution, recovering lost notes. Use when the user says "vault not committing", "git conflict in vault", "lost a note", "Obsidian Git", "auto-commit", "vault sync", or extends the vault backup strategy.
---

# obsidian-git-vault

Level 10 of the Brain progression — **Vault Immortal**. Obsidian Git plugin auto-commits the vault every 10 mins, auto-pushes to remote. The vault literally cannot lose a note for more than 10 minutes.

## How It Works

The Obsidian Git plugin (installed in the vault) runs in the Obsidian process:

```
Every 10 mins:
  ↓
git add -A         (in HYPERFOCUS_ZONE/)
git commit -m "vault: auto-commit <timestamp>"
git push origin <branch>
```

If push fails (conflict, no remote), it logs to Obsidian's notice tray but **doesn't block** — local commits still happen. Conflicts resolve next sync.

## Verify It's Running

In Obsidian:

1. Cmd+P → "Obsidian Git: Show status"
2. Should show recent auto-commits in the log
3. Cmd+P → "Obsidian Git: Pull" (manual pull)
4. Cmd+P → "Obsidian Git: Push" (manual push)

If commands aren't available → plugin not installed/enabled. Settings → Community Plugins → enable Obsidian Git.

## Plugin Config (in `.obsidian/plugins/obsidian-git/data.json`)

Canonical settings:

```json
{
  "autoCommitInterval": 10,
  "autoPushInterval": 10,
  "autoPullInterval": 0,
  "commitMessage": "vault: auto-commit {{date}}",
  "commitDateFormat": "YYYY-MM-DD HH:mm:ss",
  "pullBeforePush": true
}
```

`autoPullInterval: 0` = no auto-pull (avoids surprise merges). Pull manually when starting work on a different machine.

## Working On Multiple Machines

```
Machine A finishes work → push (auto, every 10min)
  ↓
Machine B starts work → MANUAL PULL FIRST
  ↓
Machine B works, commits queue → push (auto)
```

**Always pull first when switching machines.** Without it, you'll get merge conflicts on the next auto-commit.

```powershell
# Manual pull from anywhere
cd H:\BROski-Obsidian-Brain-for-HyperFocus-z0ne
git pull
# (Note: this is on the REPO, but the vault is inside HYPERFOCUS_ZONE/. Run git from repo root.)
```

## Recovering A Lost Note

The vault is git. Anything ever written is recoverable:

```powershell
cd H:\BROski-Obsidian-Brain-for-HyperFocus-z0ne

# Find when a file existed
git log --all --follow -- "HYPERFOCUS_ZONE/01-Projects/<file>.md"

# Show file contents at a specific commit
git show <commit>:HYPERFOCUS_ZONE/01-Projects/<file>.md

# Restore file from a specific commit
git checkout <commit> -- HYPERFOCUS_ZONE/01-Projects/<file>.md

# Find any deleted file ever
git log --all --diff-filter=D --summary | Select-String "<filename>"
```

## Conflict Resolution

If auto-commit fails with a conflict:

1. Obsidian Git shows a notice — open it
2. Files in conflict have `<<<<<<<` markers — resolve them in Obsidian or VS Code
3. After resolving:
   ```powershell
   cd H:\BROski-Obsidian-Brain-for-HyperFocus-z0ne
   git add HYPERFOCUS_ZONE/
   git commit -m "vault: resolve conflict"
   git push
   ```
4. Auto-commit resumes on next interval

**Don't try to fix conflicts inside Obsidian's editor without saving** — Obsidian Git's "View changes" diff UI helps but is read-only. Use VS Code or terminal for the actual edit.

## What's Committed

```
HYPERFOCUS_ZONE/        ← all notes, frontmatter, attachments
HYPERFOCUS_ZONE/.obsidian/  ← plugin configs, themes, hotkeys (committed = portable across machines)
```

The `.obsidian/` folder is committed — that means plugins, hotkeys, and CSS modes travel with the vault.

## What's NOT Committed (`.gitignore`)

```
.obsidian/workspace.json     # window layout (per-machine)
.obsidian/cache              # plugin cache
.trash/                      # Obsidian's local trash
```

Configure these in `H:\BROski-Obsidian-Brain-for-HyperFocus-z0ne\.gitignore`.

## Common Failures

| Symptom | Cause | Fix |
|---|---|---|
| Vault hasn't committed in hours | Obsidian closed, or plugin disabled | Open Obsidian, check plugin status |
| Push fails: "non-fast-forward" | Remote has changes you don't | Manual pull first, then push |
| Conflict marker `<<<<<<<` in a note | Concurrent edits across machines | Resolve manually, commit |
| Vault history missing | Repo not pushed to remote | Set up remote (`git remote add origin <url>`), `git push -u origin main` |
| "Not a git repository" error in Obsidian Git | `.git` folder missing | `git init` at repo root, push to remote |
| Massive commit (1000s of files) | First-time commit including media | OK — large attachments are part of the vault. Consider Git LFS for binary >50MB |
| Plugin commits secrets to git | `.env` in vault folder | Move secrets out of `HYPERFOCUS_ZONE/`, add to `.gitignore` |

## Best Practice — Repo Layout

```
H:\BROski-Obsidian-Brain-for-HyperFocus-z0ne\
├── .git/                       ← canonical git repo
├── .gitignore                  ← excludes per-machine state
├── HYPERFOCUS_ZONE/            ← the vault (Obsidian opens THIS)
├── *.py                        ← Brain modules
├── docker-compose.hyper-brain.yml
└── ...
```

**Repo root is the git repo. Vault is inside.** Obsidian Git operates on the whole repo, but only commits content under `HYPERFOCUS_ZONE/` due to `.gitignore` rules (the Brain Python files are tracked too, but don't change as often).

## Manual Backup (belt + braces)

Even with auto-commit, occasionally export a snapshot:

```powershell
cd H:\
$stamp = Get-Date -Format "yyyy-MM-dd_HHmm"
Compress-Archive `
  -Path "BROski-Obsidian-Brain-for-HyperFocus-z0ne\HYPERFOCUS_ZONE" `
  -DestinationPath "vault-backup-$stamp.zip"
```

Drop the zip in cloud storage. Belt-and-braces — the vault is already on git, but redundancy never hurts.

## Companion Skills

- `vault-para-structure` — what's getting committed
- `hyper-brain-modules` — modules write to vault, then auto-commit picks up
- `morning-briefing-ai` — briefings auto-commit within 10 mins of generation
- `level-progression` — Level 10 context

## Hard Rules

- **Pull before working on a 2nd machine** — every time
- **Don't disable auto-commit** — vault immortality depends on it
- **Don't commit `.env` files** — `.gitignore` them
- **Resolve conflicts in VS Code or terminal**, not Obsidian's editor
- **`.obsidian/` is committed** — plugins/hotkeys travel with the vault
- **Push to remote** — local-only git is one disk failure away from gone
