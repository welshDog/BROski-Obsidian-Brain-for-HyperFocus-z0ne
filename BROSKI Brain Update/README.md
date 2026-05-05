# 🧠 THE HYPER BRAIN v3.0 — HyperFocus z0ne

> Built by [@welshDog](https://github.com/welshDog) — Lyndz Williams, Llanelli, Wales 🏴󠁧󠁢󠁷󠁬󠁳󠁿  
> **Neurodivergent-first Second Brain. ADHD + Dyslexia + Autistic friendly.**  
> **Last updated: May 5, 2026 — Levels 13–20 COMPLETE ✅**

---

## 🚀 What This Is

**THE HYPER BRAIN** is the next-generation evolution of the BROski Obsidian Brain. It's not just a vault scaffold anymore — it's a **living, breathing cognitive prosthetic** that actively helps you focus, decomposes overwhelming tasks, filters distractions, and learns your patterns.

This upgrade transforms your Obsidian vault from passive storage into an **active AI-powered focus companion** with:

- 🧠 **Real-time focus tracking** with adaptive DifficultyDial
- 🤖 **AI-powered morning briefings** with predictive prioritization
- 🪓 **HyperSplit task decomposition** — break the impossible into the inevitable
- 🛡️ **AI distraction filtering** — learns your patterns, suggests interventions
- 📊 **Deep analytics** — focus heatmaps, streaks, weekly reports
- 🌐 **Real-time GitHub webhooks** — issues + PRs instantly in your inbox
- 🔗 **MCP bridge** — local LLM integration for vault RAG + agent conversations
- 📸 **Session snapshots** — never lose context again
- 🎮 **Dynamic gamification** — DifficultyDial + streak recovery tokens

---

## 🏗️ Vault Structure (v3.0)

```
HYPERFOCUS_ZONE/
├── 00-Inbox/
│   ├── GitHub/              # Real-time webhook issues + PRs
│   ├── Briefings/           # AI-generated morning briefings
│   └── AI-Capture/          # Voice → atomic notes (future)
├── 01-Projects/             # Active builds + HyperSplit tasks
├── 02-Areas/
│   ├── Health/
│   ├── Admin/
│   ├── DevOps/
│   └── Focus-Analytics/     # Weekly reports, heatmaps, trends
├── 03-Resources/
│   ├── Snippets/
│   ├── Economy/
│   ├── Agents/              # Agent config YAMLs
│   └── MCP/                 # MCP server configs
├── 04-Archive/              # Done wins
├── 05-Focus-Sessions/       # Session logs with YAML metrics
├── 06-AI-Context/
│   └── snapshots/           # Session state captures
├── 07-Streaks-Achievements/ # Dynamic streaks + recovery tokens
├── 99-Templates/
│   ├── Daily.md             # + focus_intent, distraction_log
│   ├── Project.md           # + focus_budget, complexity_score
│   ├── Focus-Session.md     # Session template with metrics
│   ├── Task-HyperSplit.md   # Recursive micro-task tree
│   ├── Morning-Briefing.md  # AI-enhanced predictive briefing
│   └── Weekly-Analytics.md  # Auto-generated focus report
└── Hub/
    ├── Dashboard.md         # Live: focus score, streak, pet status
    ├── Focus-Command-Center.md  # API commands + quick actions
    ├── Maps-of-Content.md
    └── Brain-Constellation.md   # Visual ecosystem map
```

---

## ⚡ Features (v3.0)

| Feature | Status | Level |
|---------|--------|-------|
| 🔄 Obsidian Git auto-sync (10 min) | ✅ LIVE | 10 |
| 💰 BROski$ Coin Tracker + XP | ✅ LIVE | 11 |
| ⏰ Pomodoro + Focus/Calm/Hyper Mode | ✅ LIVE | 12 |
| 🐛 GitHub Issues → Inbox (4 repos) | ✅ LIVE | 9 |
| 🌅 Morning Briefing template | ✅ Ready | 13 |
| 🎮 20 Levels + XP system | ✅ Built-in | 20 |
| 🐳 Docker github-sync container | ✅ Ready | 9 |
| 🛠️ setup.ps1 one-run bootstrap | ✅ Ready | 12 |
| 🧠 **Real-time focus tracking** | ✅ **NEW** | 16 |
| 🤖 **AI Morning Briefing** | ✅ **NEW** | 13–15 |
| 🪓 **HyperSplit decomposition** | ✅ **NEW** | 17 |
| 🛡️ **AI distraction filter** | ✅ **NEW** | 18 |
| 📊 **Focus analytics + heatmaps** | ✅ **NEW** | 16 |
| 🔗 **MCP local LLM bridge** | ✅ **NEW** | 15 |
| 📸 **Session snapshots** | ✅ **NEW** | 16 |
| 🌐 **GitHub webhooks real-time** | ✅ **NEW** | 14 |
| 🎮 **DifficultyDial + streak recovery** | ✅ **NEW** | 19 |

---

## 🎮 Level Tracker

- [x] **Level 1–8** — Vault + folders + plugins ✅
- [x] **Level 9** — GitHub bridge LIVE 🌉 ✅ *May 5*
- [x] **Level 10** — Vault immortal (Obsidian Git) 🔒 ✅ *May 5*
- [x] **Level 11** — BROski$ flowing 💰 ✅ *May 5*
- [x] **Level 12** — Hyperfocus Mode armed ⚡ ✅ *May 5*
- [x] **Level 13** — Morning Briefing AI ✅ *May 5*
- [x] **Level 14** — GitHub Webhooks real-time ✅ *May 5*
- [x] **Level 15** — HyperAgent AI Daily Briefing ✅ *May 5*
- [x] **Level 16** — Focus Tracker + Analytics ✅ *May 5*
- [x] **Level 17** — HyperSplit Task Decomposition ✅ *May 5*
- [x] **Level 18** — AI Distraction Filter ✅ *May 5*
- [x] **Level 19** — DifficultyDial + Dynamic Gamification ✅ *May 5*
- [x] **Level 20** — THE HYPER BRAIN Constellation ✅ *May 5*

---

## 🛠️ Setup

### Prerequisites
- Python 3.11+
- Docker + Docker Compose
- Obsidian.md
- GitHub PAT (fine-grained token)

### Quick Start

```powershell
# 1. Clone the repo
git clone https://github.com/welshDog/THE-HYPER-BRAIN.git
cd THE-HYPER-BRAIN

# 2. Run enhanced setup
.\scripts\setup_hyper_brain.ps1

# 3. Install Python dependencies
pip install -r docker/requirements.txt

# 4. Configure environment
# Create .env file:
GITHUB_PAT=ghp_xxxxxxxx
GITHUB_WEBHOOK_SECRET=your_webhook_secret
OBSIDIAN_VAULT_PATH=C:\Users\Lyndz\Obsidian\HYPERFOCUS_ZONE
REDIS_URL=redis://localhost:6379/4
MCP_PORT=8099

# 5. Start THE HYPER BRAIN (container #30)
docker compose -f docker/docker-compose.hyper-brain.yml up -d

# 6. Verify
Invoke-RestMethod -Uri "http://localhost:8100/health"
# → {"status":"hyper","version":"3.0.0","level":20,"containers":30}

# 7. Open vault in Obsidian
# Settings → Appearance → CSS Snippets → hyper-brain-themes.css ✅
```

### Hotkeys
| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+F` | Toggle Focus Mode |
| `Ctrl+Shift+E` | End Focus Session |
| `Ctrl+Shift+M` | Generate Morning Briefing |
| `Ctrl+Shift+S` | Emergency Snapshot |
| `Ctrl+Shift+H` | HyperSplit current task |

---

## 🐳 The 30th Container: `hyper-brain`

```
hyper-brain (port 8100)
├── hyper_brain_core.py      # FastAPI orchestrator
├── focus_tracker.py          # File watcher + adaptive sessions
├── ai_distraction_filter.py  # Context scoring + interventions
├── hyper_split.py            # Recursive task decomposition
├── mcp_bridge.py             # Local LLM gateway (LMStudio/Ollama)
├── analytics_engine.py       # Reports + streaks + heatmaps
├── github_webhook_server.py  # Real-time webhook receiver
├── morning_briefing_ai.py    # AI briefing generator
└── session_snapshot.py       # State capture + recovery
```

**Resource Limits**: 256MB RAM, 0.5 CPU cores  
**Health Check**: Every 30s via `/health`  
**Networks**: `app-net`, `agent-net` (shared with HyperCode-V2.4)

---

## 🔗 API Reference

### Focus Sessions
```powershell
# Start
POST http://localhost:8100/focus/start
Body: {"intent":"Build API","estimated_minutes":25,"project":"HyperCode","difficulty_preference":"auto"}

# End
POST http://localhost:8100/focus/end
Body: {"session_id":"abc123","actual_minutes":30,"mood":8}

# Status
GET http://localhost:8100/focus/status

# Snapshot
POST http://localhost:8100/focus/snapshot
```

### HyperSplit
```powershell
POST http://localhost:8100/hypersplit
Body: {"task_title":"Implement Stripe","task_description":"...","max_depth":3}
```

### Analytics
```powershell
GET http://localhost:8100/analytics/weekly
GET http://localhost:8100/analytics/streaks
GET http://localhost:8100/analytics/heatmap?days=30
```

### Morning Briefing
```powershell
POST http://localhost:8100/briefing/generate
Body: {"date":"2026-05-05","include_ai_suggestions":true}
```

### MCP / Local LLM
```powershell
POST http://localhost:8100/mcp/query
Body: {"query":"What are my overdue tasks?"}
```

### Distractions
```powershell
POST http://localhost:8100/distraction/report
Body: {"source":"social_media","context":"Twitter notification"}

GET http://localhost:8100/distraction/patterns?days=7
```

---

## 🧠 Neurodivergent-First Design

| Need | Solution |
|------|----------|
| **Time blindness** | Adaptive Pomodoro + time-blindness alerts + transition buffers |
| **Executive dysfunction** | HyperSplit decomposition + AI prioritization + session snapshots |
| **Distractibility** | AI distraction filter + pattern learning + intervention suggestions |
| **Dyslexia** | OpenDyslexic font + high contrast + line-height 1.9 + letter-spacing |
| **Sensory overload** | Calm mode + gradual transitions + overload detection |
| **Dopamine regulation** | DifficultyDial + instant XP + streak recovery + pet rewards |
| **Context loss** | Session snapshots + morning briefings + brain state recovery |
| **Task overwhelm** | Recursive micro-task decomposition + focus budgets |

---

## 🔒 Security & Data Sovereignty

- **Local-First**: All LLM inference via LMStudio/Ollama MCP — zero cloud telemetry
- **Webhook Validation**: GitHub webhooks verified via HMAC-SHA256
- **API Keys**: Docker secrets pattern; `.env` never committed
- **MCP Sandboxing**: File system access restricted to vault path only
- **No Corporate AI**: Your thoughts stay on your machine. Always.

---

## 🎮 Gamification: DifficultyDial Algorithm

THE HYPER BRAIN implements a **real-time adaptive difficulty** system:

1. **Monitors** your activity density (file edits, keystrokes, idle time)
2. **Calculates** flow score (0.0–1.0) every 2 minutes
3. **Adjusts**:
   - Flow > 0.8 → Extends Pomodoro (+10 min, max 2 extensions)
   - Idle > 2 min → Shortens Pomodoro (suggests break)
   - Error rate spikes → Reduces difficulty
4. **Awards** BROski$ + XP based on flow score + difficulty + mood
5. **Recovery tokens** preserve streaks when life happens

---

## 📊 Analytics Dashboard

Live metrics in your vault:
- **Focus heatmap**: When you focus best (hour × day)
- **Project distribution**: Where your time goes
- **Distraction patterns**: What breaks your flow + when
- **Streak tracking**: Current + longest + recovery tokens
- **Weekly reports**: Auto-generated every Monday

---

## 🔗 Ecosystem Links

- [HyperCode-V2.4](https://github.com/welshDog/HyperCode-V2.4)
- [HyperAgent-SDK](https://github.com/welshDog/HyperAgent-SDK)
- [Hyper-Vibe-Coding-Course](https://github.com/welshDog/Hyper-Vibe-Coding-Course)
- [BROskiPets-LLM-dNFT](https://github.com/welshDog/BROskiPets-LLM-dNFT)

---

## 🙏 Credits

> *"You built the future people keep saying they want. You actually did it."*  
> — Gordon, Docker AI · Grade A Review 🏅

**Built with 🧠 + ❤️ + ♾ in Llanelli, Wales 🏴󠁧󠁢󠁷󠁬󠁳󠁿**

*by [@welshDog](https://github.com/welshDog) — Lyndz Williams*

**A BROski is ride or die. We build this together. 🐶♾️🔥**

---

## 📜 License

MIT — Build your own brain. Share the love.
