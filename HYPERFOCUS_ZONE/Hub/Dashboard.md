# 🧠 BROski♾️ Brain — Hyperfocus Zone Dashboard

> One view. All projects. Always know your next move.

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

## 🐛 GitHub Issues (Live)

```dataview
TASK
FROM "00-Inbox/GitHub"
WHERE !completed
GROUP BY file.name
SORT file.ctime DESC
```

---

## 📅 Today's Notes

```dataview
LIST
FROM "00-Inbox"
WHERE file.ctime >= date(today)
SORT file.ctime DESC
```

---

## 🎉 Recent Wins

```dataview
LIST
FROM "04-Archive"
SORT file.mtime DESC
LIMIT 5
```
