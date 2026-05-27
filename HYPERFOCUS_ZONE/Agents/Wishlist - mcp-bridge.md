---
type: agent-wishlist
title: Wishlist - mcp-bridge
agent: mcp-bridge
status: active
priority_focus: tier-1
created: 2026-05-27
updated: 2026-05-27
tags:
  - wishlist
  - agent
  - mcp-bridge
---

# Wishlist - mcp-bridge

## Role (What I Do)
- I route tool calls between agents and external systems.
- I keep the agent cluster **talking cleanly**.
- I block unsafe calls.

## What I Want In The Brain (Top 3)
- A single **Tools Registry** note listing supported tools + what they touch.
- A single **Secrets Policy** note (what never enters the vault).
- A clear "allowed integrations" list (GitHub, Discord, Claude, Stripe).

## Inputs I Need (Signals/Data)
- Tool schemas and tool capabilities per agent.
- Runtime environment constraints (ports, networks, rate limits).
- Integration configs stored as variables, not notes.

## Outputs I Produce (Notes/Events)
- A human-readable tool catalog for builders.
- Alert notes when integrations fail.
- A minimal changelog when new tools are added.

## Rules I Must Respect
- Never log secrets.
- Never write tokens into notes.
- Prefer stable schemas over vibes.

## Next Upgrades (Tier 1 → Tier 3)
- **Tier 1:** Add a Tools Registry note and enforce naming conventions.
- **Tier 2:** Add integration health notes (GitHub, Discord, LLM).
- **Tier 3:** Add a tool budget policy (rate limit + cost guardrails).
