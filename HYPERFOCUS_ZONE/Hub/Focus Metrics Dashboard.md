---
type: dashboard
title: Focus Metrics Dashboard
status: active
owner: focus-tracker
tags:
  - dashboard
  - focus
  - metrics
  - dataview
created: 2026-05-27
updated: 2026-05-27
---

# 📊 Focus Metrics Dashboard

> Key numbers. No fluff. Updated by focus-tracker agent.

## Recent Sessions

```dataview
TABLE task AS Task, duration_mins AS "Mins", score AS Score, date AS Date
FROM "05-Focus-Sessions"
SORT date DESC
LIMIT 10
```

## Weekly Rollup

```dataview
TABLE rows.file.name AS Sessions, length(rows) AS Count
FROM "05-Focus-Sessions"
GROUP BY dateformat(date(date), "YYYY-WW") AS Week
SORT Week DESC
LIMIT 6
```

## Streak & Achievements
- See [[07-Streaks-Achievements]] for full history.

## 3 Key Metrics to Watch
- **Avg session score this week:** (fill from rollup)
- **Longest streak:** (fill from streaks note)
- **Top distraction pattern:** (fill from session logs)
