# 🧠 BROski♾️ Brain — Hyperfocus Zone Dashboard

> One view. All projects. Always know your next move.
> 🔗 [[Hub/War-Room.canvas|War Room]] · [[Hub/Today Focus]] · [[Hub/Focus-Command-Center]] · [[Hub/Brain-Constellation-Live]]

---

## 🎯 Today → [[Hub/Today Focus]]

---

## 🔥 Active Projects

```dataview
TABLE status, file.mtime AS "Last Updated"
FROM "01-Projects"
WHERE project = true AND status != "done"
SORT file.mtime DESC
```

---

## 💰 BROski$ This Week

```dataviewjs
const pages = dv.pages('"01-Projects" OR "00-Inbox"')
  .where(p => p.status === "done");
const coins = pages.map(p => p.coins || 0).array().reduce((a,b) => a+b, 0);
const xp = pages.map(p => p.xp || 0).array().reduce((a,b) => a+b, 0);
dv.paragraph(`### 💰 ${coins} BROski$ | ⭐ ${xp} XP earned total`);
```

---

## ⚠️ Blockers

```dataview
LIST
FROM #type/blocker AND -#status/done
SORT file.mtime DESC
```

---

## 🐛 GitHub Issues (Live)

```dataview
TASK
FROM "00-Inbox/GitHub"
WHERE !completed
GROUP BY file.name
SORT file.ctime DESC
```

---

## 📅 Recent Notes

```dataview
LIST
FROM "00-Inbox"
WHERE file.ctime >= date(today) - dur(7 days)
SORT file.ctime DESC
LIMIT 10
```

---

## 📊 Focus Sessions This Week

```dataview
TABLE duration AS "Duration", xp_earned AS "XP"
FROM "05-Focus-Sessions"
WHERE file.ctime >= date(today) - dur(7 days)
SORT file.ctime DESC
```

---

## 🩺 Quick Links

| Area | Link |
|---|---|
| 🩺 Health | [[02-Areas/Health/Health-Dashboard]] |
| 📋 Admin | [[02-Areas/Admin/Admin-Radar]] |
| 🐳 DevOps | [[02-Areas/DevOps/DevOps-Runbook]] |
| 🏷️ Tags | [[03-Resources/Tag-Architecture]] |
| 🔌 Plugins | [[03-Resources/Recommended-Plugins]] |
| ⚡ Focus Commands | [[Hub/Focus-Command-Center]] |
| 🌌 Constellation | [[Hub/Brain-Constellation-Live]] |

---

## 🎉 Recent Wins

```dataview
LIST
FROM "04-Archive"
SORT file.mtime DESC
LIMIT 5
```

---

> 🧠⚡ HYPER BRAIN v3.0 — [[Hub/War-Room.canvas|Open War Room]] for full visual command center
