---
type: index
title: Agent Wishlists (Index)
tags:
  - index
  - agent-wishlist
created: 2026-05-27
updated: 2026-05-27
---

# Agent Wishlists (Index)

One page. All agent wants. Fast scan.

```dataview
TABLE agent AS Agent, priority_focus AS Tier, status AS Status, updated AS Updated
FROM "HYPERFOCUS_ZONE/Agents"
WHERE type = "agent-wishlist"
SORT priority_focus ASC, updated DESC
```
