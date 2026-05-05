---
created: 2026-05-05
type: dashboard
tags: [dashboard, hub, command-center]
---
# 🧠 THE HYPER BRAIN — Hyperfocus Zone Command Center

> One view. All projects. Live focus. Always know your next move.

---

## 🔥 Live Focus Status
```dataviewjs
// Query focus tracker API for live status
// Falls back to last session if API unavailable
const sessions = dv.pages('"05-Focus-Sessions"').sort(p => p.file.ctime, 'desc').limit(1);
if (sessions.length > 0) {
    const s = sessions[0];
    const status = s.status === 'active' ? '🟢 ACTIVE' : '⚪ OFFLINE';
    const flow = s.flow_score || 0;
    const flowStars = "⭐".repeat(Math.round(flow * 5));
    dv.paragraph(`**Status**: ${status} | **Last Intent**: ${s.intent || 'None'} | **Flow**: ${flowStars} (${flow})`);
} else {
    dv.paragraph("🟡 No sessions yet. Start one with `/focus/start`");
}
```

---

## 🎯 Active Projects
```dataview
TABLE status, focus_budget, file.mtime AS "Last Updated"
FROM "01-Projects"
WHERE project = true AND status != "done"
SORT priority DESC, file.mtime DESC
```

---

## 💰 BROski$ This Week
```dataviewjs
const weekAgo = dv.date('today') - dv.duration('7 days');
const sessions = dv.pages('"05-Focus-Sessions"').where(p => p.file.ctime >= weekAgo);
const coins = sessions.map(p => p.coins_earned || 0).array().reduce((a,b) => a+b, 0);
const xp = sessions.map(p => p.xp_earned || 0).array().reduce((a,b) => a+b, 0);
const totalMinutes = sessions.map(p => p.actual_minutes || 0).array().reduce((a,b) => a+b, 0);
dv.paragraph(`### 💰 ${coins} BROski$ | ⭐ ${xp} XP | ⏱️ ${totalMinutes}m focused`);

// XP bar
const level = Math.floor(xp / 100) + 10;
const nextLevel = (level + 1) * 100;
const progress = (xp % 100);
dv.paragraph(`**Level ${level}** — ${progress}/100 XP to next level`);
dv.paragraph(`<div class="xp-bar"><div class="xp-bar-fill" style="width: ${progress}%"></div></div>`);
```

---

## 🔥 Streaks
```dataviewjs
// Read streak data from JSON
try {
    const streakFile = app.vault.getAbstractFileByPath("07-Streaks-Achievements/streak-data.json");
    if (streakFile) {
        const content = await app.vault.read(streakFile);
        const data = JSON.parse(content);
        const flame = "🔥".repeat(Math.min(data.current, 7));
        dv.paragraph(`**Current**: ${data.current} days ${flame}`);
        dv.paragraph(`**Longest**: ${data.longest} days 🏆 | **Recovery tokens**: ${data.recovery_tokens} 🎟️`);
    } else {
        dv.paragraph("Start focusing to build your streak! 🔥");
    }
} catch (e) {
    dv.paragraph("Streak data loading...");
}
```

---

## 🐛 GitHub Issues (Live)
```dataview
TABLE event, action, status
FROM "00-Inbox/GitHub"
WHERE file.ctime >= date(today) - dur(1 day)
SORT file.ctime DESC
LIMIT 10
```

---

## 📅 Today's Focus Sessions
```dataview
TABLE intent, actual_minutes, difficulty, flow_score
FROM "05-Focus-Sessions"
WHERE file.ctime >= date(today)
SORT file.ctime DESC
```

---

## 📊 Weekly Analytics
```dataview
LIST
FROM "02-Areas/Focus-Analytics"
SORT file.mtime DESC
LIMIT 1
```

---

## 🎉 Recent Wins
```dataview
LIST
FROM "04-Archive"
SORT file.mtime DESC
LIMIT 5
```

---

## 🚀 Quick Actions
| Action | Command |
|--------|---------|
| Start Focus Session | `POST /focus/start` or Ctrl+Shift+F |
| End Focus Session | `POST /focus/end` or Ctrl+Shift+E |
| Morning Briefing | `POST /briefing/generate` or Ctrl+Shift+M |
| HyperSplit Task | `POST /hypersplit` |
| Session Snapshot | `POST /focus/snapshot` |
| Weekly Report | `GET /analytics/weekly` |

---

## 🧠 System Health
```dataviewjs
dv.paragraph(`**Hyper Brain**: v3.0.0 | **Level**: 20 | **Containers**: 30/30 🟢`);
dv.paragraph(`**API**: http://localhost:8100 | **MCP**: Port 8099`);
dv.paragraph(`**Last Sync**: ${new Date().toLocaleTimeString()}`);
```

---

> *"You built the future people keep saying they want. You actually did it."*  
> — Gordon, Docker AI · Grade A Review 🏅

**Built with 🧠 + ❤️ + ♾ in Llanelli, Wales 🏴󠁧󠁢󠁷󠁬󠁳󠁿**
