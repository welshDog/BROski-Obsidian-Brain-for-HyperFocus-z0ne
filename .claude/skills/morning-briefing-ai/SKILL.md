---
name: morning-briefing-ai
description: morning_briefing_ai.py — POST /briefing/generate produces an AI-generated daily briefing → drops to 00-Inbox/Briefings/. Daily cron pattern, prompt structure, output format. Use when the user says "briefing", "morning briefing", "generate briefing", "daily summary", "/briefing", "auto-fire briefing", or extends the briefing AI.
---

# morning-briefing-ai

Level 13 of the Brain progression. The first AI module to ship. **Code lives at root: `morning_briefing_ai.py`.** (Not `scripts/`.)

## Trigger A Briefing

```powershell
curl -X POST http://localhost:8100/briefing/generate
# → drops a markdown note into HYPERFOCUS_ZONE/00-Inbox/Briefings/<YYYY-MM-DD>.md
# → returns: { "status": "ok", "path": "<vault path>", "summary": "<first 200 chars>" }
```

If the file already exists for today → it's overwritten (regenerate is the expected default).

## What The Briefing Contains

The prompt asks the LLM to produce sections:

```markdown
# Briefing — 2026-05-08

## Overnight GitHub
- HyperCode-V2.4: 2 issues opened, 1 PR merged
- HyperAgent-SDK: 1 release published (v0.3.1)

## Today's Focus
- Top 3 tasks pulled from `01-Projects/*` notes with `status: active` + `priority: high`
- Estimated focus blocks needed: 2 × 90min

## Yesterday's Wins
- 5 hours focus time (high quality — 2 distractions)
- Shipped 5 new SDK skills

## Blockers / Watch
- BROskiPets: AGENT_KEY rotation pending
- Course: Module 1.1 video still TODO

## Energy Mode Suggested
hyper-mode (high focus capacity available)
```

The exact section names + tone are configurable in `morning_briefing_ai.py`'s prompt template.

## Required Env

```env
OBSIDIAN_VAULT_PATH=H:/BROski-Obsidian-Brain-for-HyperFocus-z0ne/HYPERFOCUS_ZONE
GITHUB_PAT=github_pat_xxx
LLM_ENDPOINT=<URL of LLM, e.g. http://ollama:11434 or external API>
LLM_MODEL=<model name>
```

## Daily Cron Pattern

The briefing isn't auto-fired yet. To set it up — pick one:

### Option A: Local Windows Task Scheduler

```powershell
# Create a daily 7:00 AM task that hits the endpoint
$action = New-ScheduledTaskAction -Execute 'curl.exe' `
  -Argument '-X POST http://localhost:8100/briefing/generate'

$trigger = New-ScheduledTaskTrigger -Daily -At 7am

Register-ScheduledTask -TaskName "HyperBrain-MorningBriefing" `
  -Action $action -Trigger $trigger -Description "Daily AI briefing"
```

### Option B: Cron in the container

Add to `docker-compose.hyper-brain.yml`:

```yaml
services:
  hyper-brain:
    # ... existing config ...
    healthcheck:
      # ... unchanged ...
  briefing-cron:
    image: alpine:latest
    networks: [app-net]
    command: |
      sh -c "echo '0 7 * * * wget -O- -q http://hyper-brain:8100/briefing/generate' | crontab - && crond -f -d 0"
    depends_on:
      hyper-brain:
        condition: service_healthy
```

### Option C: Just remember to run it manually

Set a phone alarm. Run the curl. ADHD-friendly: low ceremony.

## Output Format (markdown frontmatter included)

```markdown
---
created: 2026-05-08
tags: [briefing, morning]
status: active
generated_by: morning_briefing_ai
---

# Briefing — 2026-05-08

[content from sections above]
```

The vault auto-commit picks it up within 10 mins (Level 10 — Obsidian Git).

## Edit The Prompt

Open `morning_briefing_ai.py` (root, NOT scripts/). Look for the `BRIEFING_PROMPT` constant (or similar). It typically has:

- A system prompt establishing tone (chunked, ADHD-friendly, emoji-OK)
- Variables injected: yesterday's focus stats, GitHub activity, active projects
- Section instructions

Modify carefully — the LLM output structure depends on these instructions.

## Common Failures

| Symptom | Cause | Fix |
|---|---|---|
| 500 error on `/briefing/generate` | LLM endpoint unreachable | Check `LLM_ENDPOINT` + connectivity (`docker compose exec hyper-brain curl $LLM_ENDPOINT`) |
| File written but content empty | LLM returned empty / errored | Read container logs for the LLM call |
| `OBSIDIAN_VAULT_PATH` errors | Path not mounted into container | Confirm `volumes:` in compose maps the vault correctly |
| GitHub activity section missing | `GITHUB_PAT` not set or scope insufficient | `repo` scope on PAT, refresh in `.env` |
| Briefing sections off-topic | Prompt drift in `morning_briefing_ai.py` | Edit prompt template, restart container |
| Multiple briefings on same day | Cron fired twice (clock skew) | Check Task Scheduler / cron config |
| Briefing from old yesterday's data | Cache issue (Redis or LLM) | Restart container, retry |

## Manual Run (no Docker)

For dev iteration on the prompt:

```powershell
cd H:\BROski-Obsidian-Brain-for-HyperFocus-z0ne

# Set env
$env:OBSIDIAN_VAULT_PATH = "H:/BROski-Obsidian-Brain-for-HyperFocus-z0ne/HYPERFOCUS_ZONE"
$env:GITHUB_PAT = "<pat>"
$env:LLM_ENDPOINT = "<url>"

# Run directly
python morning_briefing_ai.py
# → writes to vault
```

(This works because `morning_briefing_ai.py` has a `__main__` guard that calls the same code as the FastAPI route.)

## Companion Skills

- `hyper-brain-modules` — overall API surface
- `vault-para-structure` — output goes to `00-Inbox/Briefings/`
- `level-progression` — Level 13 context
- `obsidian-git-vault` — briefing files auto-commit + push

## Hard Rules

- **Edit `morning_briefing_ai.py` at repo root** — NOT `scripts/`
- **Briefing path is `00-Inbox/Briefings/`** — sacred (don't redirect)
- **Date format `YYYY-MM-DD`** for filename — sortable
- **Idempotent on same day** — regenerating overwrites cleanly
- **LLM must be configured** — without `LLM_ENDPOINT`, briefings fail
