---
created: <% tp.date.now("YYYY-MM-DD") %>
tags: [daily, briefing]
---
# 🌅 Morning Briefing — <% tp.date.now("ddd Do MMM") %>

## 🎯 Top 3 Today
- [ ] 
- [ ] 
- [ ] 

## 🐛 GitHub Issues
![[00-Inbox/GitHub/HyperCode-V2.4]]

## 💰 BROski$ Balance
```dataviewjs
const done = dv.pages('"01-Projects"').where(p => p.status === "done");
const coins = done.map(p => p.coins || 0).array().reduce((a,b) => a+b, 0);
dv.paragraph(`💰 ${coins} BROski$ earned total`);
```

## 🐳 Docker Status
- [ ] Run: `docker compose ps` — target 29/29 healthy

## 🧠 Brain Dump
-

## 🎉 Yesterday's Win
-
