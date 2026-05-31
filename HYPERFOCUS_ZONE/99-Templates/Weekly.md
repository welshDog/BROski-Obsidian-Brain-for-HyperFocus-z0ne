---
type: weekly-review
title: "Weekly Review — {{date:gggg-[W]ww}}"
week: "{{date:gggg-[W]ww}}"
tags:
  - review
  - weekly
created: "{{date:YYYY-MM-DD}}"
---

# 📊 Weekly Review — {{date:gggg-[W]ww}}

> Reflect for 5 mins. Celebrate wins. Adjust course. Move on.

---

## 🏆 Wins This Week
> What shipped? What worked? Even small stuff counts.

- 

---

## 📈 Focus Sessions

```dataview
TABLE duration AS "Duration", xp_earned AS "XP"
FROM "05-Focus-Sessions"
WHERE file.ctime >= date(today) - dur(7 days)
SORT file.ctime DESC
```

---

## 🧠 What I Learned / Realised

- 

---

## ⚠️ What Didn't Work

- 

---

## 💰 BROski$ This Week

| | Amount |
|---|---|
| Start balance | |
| Earned | |
| Spent | |
| End balance | |

---

## 🎯 Top 3 for Next Week

1. 
2. 
3. 

---

## 🔋 Energy Check

How was my energy this week overall?
> ☀️ Great | 🌤️ Okay | ☁️ Low | ⛈️ Rough

What helped:
- 

What drained:
- 

---

> 💡 Move completed items to [[04-Archive]] · Link blockers to projects in [[01-Projects]]
