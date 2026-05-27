---
type: dashboard
title: Focus Metrics Dashboard
status: active
tags: [focus, metrics, dashboard]
created: 2026-05-27
updated: 2026-05-27
---

# 📊 Focus Metrics Dashboard

## Last 15 Sessions

```dataview
TABLE created, ended, project, intent, status, actual_minutes, estimated_minutes, mood, difficulty, flow_score, coins_earned, xp_earned
FROM "05-Focus-Sessions"
WHERE contains(file.name, "Session_")
SORT created DESC
LIMIT 15
```

## Last 7 Days (XP + BROski$)

```dataviewjs
const pages = dv.pages('"05-Focus-Sessions"')
  .where(p => p.created && p.xp_earned != null && p.coins_earned != null);

const cutoff = dv.date("today").minus({ days: 7 });
const last7 = pages.where(p => dv.date(p.created) >= cutoff);

const xp = last7.map(p => p.xp_earned).array().reduce((a,b) => a + b, 0);
const coins = last7.map(p => p.coins_earned).array().reduce((a,b) => a + b, 0);

dv.paragraph(`**Last 7 days:** ⭐ ${xp} XP | 💰 ${coins} BROski$`);
```

## How To Read This
- Flow score trending up = you’re locking in.
- Abandoned sessions are data, not failure.
- Low `file_events` + long `idle time` = friction or distraction.

