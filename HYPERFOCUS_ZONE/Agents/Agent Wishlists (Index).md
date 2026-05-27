# Agent Wishlists (Index)

One page. All agent wants. Fast scan.

```dataview
TABLE agent AS Agent, priority_focus AS Tier, updated AS Updated
FROM "HYPERFOCUS_ZONE/Agents"
WHERE type = "agent-wishlist"
SORT priority_focus ASC, updated DESC
```

