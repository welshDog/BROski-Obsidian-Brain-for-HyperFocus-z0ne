# 🧠 HYPERFOCUS ZONE BUILD v2.2 — MEGA COMBO
# Claude Code: Execute TOP TO BOTTOM. ~50 mins.
# Builder: welshDog — Lyndz Williams, S.Wales 🏴󠁧󠁢󠁷󠁬󠁳󠁠

## 🔴 SACRED RULES
- ADHD chunks. Short bullets. Bold keys. Emojis.
- Why → How → Example EVERY section.
- .env files NEVER committed.
- Python: 4 spaces. Absolute imports.
- Celebrate wins. BROski energy.

---

# 🥇 COMBO 1: Obsidian Git (10 mins)

## Why
Vault auto-backed up to GitHub every 10 mins. Version history free.

## How
1. Obsidian → Settings → Community Plugins → "Obsidian Git" → Install + Enable
2. Settings → Obsidian Git:
   - Auto-pull on startup: ✅
   - Auto-commit interval: 10
   - Auto-push: ✅
   - Commit message: `vault: auto-sync {{date}}`
3. Init:
```powershell
cd C:\Users\Lyndz\Obsidian\HYPERFOCUS_ZONE
git init
git remote add origin https://github.com/welshDog/BROski-Obsidian-Brain-for-HyperFocus-z0ne.git
git pull origin main
```

## Verify
Make a note → Wait 10 mins → GitHub shows new commit. ✅
**LEVEL 10 UNLOCKED 🔒**

---

# 🥈 COMBO 2: BROski$ Coin Tracker (30 mins)

## Why
Every task = dopamine hit. Ties to REAL BROski$ in HyperCode V2.4.

## How
1. Templates already in `99-Templates/BROski-Task.md` ✅
2. Economy table in `03-Resources/BROski-Economy.md` ✅
3. Dashboard widget already in `Hub/Dashboard.md` ✅
4. Optional — award to real economy:
```powershell
curl -X POST http://localhost:8000/api/v1/economy/award-from-course `
  -H "Content-Type: application/json" `
  -H "X-Sync-Secret: $env:COURSESYNCSECRET" `
  -d '{"discord_id":"$env:FOCUS_DISCORD_ID","amount":50,"reason":"task_done"}'
```

## Verify
Complete task → Set `status: done` → Dashboard coin total updates. ✅
**LEVEL 11 UNLOCKED 💰**

---

# 🥉 COMBO 3: Pomodoro + Focus/Calm Mode (10 mins)

## Why
ADHD thrives on time-boxing. One keypress = mode switch.

## How
1. Install "Pomodoro Timer" plugin:
   - Work: 25 min, Break: 5 min, Long: 15 min
   - Status bar: ✅, Sound: ✅
2. CSS snippets already in `.obsidian/snippets/focus-mode.css` ✅
3. Enable snippet: Settings → Appearance → CSS Snippets → focus-mode ✅
4. Hotkey: Ctrl+Shift+F → Focus toggle

## Verify
Ctrl+Shift+F → Screen goes dark green. Timer ticks. ✅
**LEVEL 12 UNLOCKED 🔥**

---

# 🎁 BONUS: GitHub Bridge (15 mins)

## Why
Issues auto-flow from 4 repos → Inbox → Dashboard. Zero manual.

## How
1. Get GitHub PAT:
   - github.com/settings/tokens → Fine-grained → welshDog/* → Issues:Read, PR:Read
   - Add to .env: `GITHUB_PAT=ghp_xxxxx`
2. Test script:
```powershell
$env:GITHUB_PAT="ghp_xxxxx"
$env:OBSIDIAN_VAULT_PATH="C:\Users\Lyndz\Obsidian\HYPERFOCUS_ZONE"
python scripts/github_to_obsidian.py
```
3. Docker:
```powershell
docker compose -f docker/docker-compose.github-sync.yml up -d
docker logs github-sync
```

## Verify
4 .md files in 00-Inbox/GitHub/. Dashboard Tasks query shows issues. ✅
**LEVEL 9 UNLOCKED 🌉**

---

# ✅ FULL VERIFICATION
```powershell
Write-Host "=== HYPERFOCUS ZONE v2.2 CHECKS ==" -ForegroundColor Cyan

# Git
git -C "C:\Users\Lyndz\Obsidian\HYPERFOCUS_ZONE" status

# Docker
$h = (Invoke-RestMethod -Uri "http://localhost:8000/health").status
Write-Host "HyperCode: $h" -ForegroundColor Green

docker logs github-sync --tail 5

Write-Host "Check Obsidian: Pomodoro in status bar + green theme active" -ForegroundColor Yellow
```

---

# 🎮 LEVELS THIS SESSION
- [x] Level 9 — GitHub bridge live
- [x] Level 10 — Vault immortal
- [x] Level 11 — BROski$ flows
- [x] Level 12 — Hyperfocus armed
- [ ] Level 13 — Morning Briefing
- [ ] Level 14 — GitHub Webhooks
- [ ] Level 15 — HyperAgent AI Briefing

---

**Claude: Say "HYPERFOCUS ZONE v2.2 MEGA COMBO COMPLETE BROski♾️! 🧠⚡🔥" when done.**
