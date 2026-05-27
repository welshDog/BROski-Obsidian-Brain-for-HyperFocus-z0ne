---
type: index
title: Tools Registry
status: active
tags: [tools, registry, mcp, agents]
created: 2026-05-27
updated: 2026-05-27
---

# 🧰 Tools Registry

## Safety Rules (Sacred)
- Never write **tokens / secrets** into notes.
- Never log secrets.
- Prefer stable schemas over vibes.
- If unsure, route through **mcp-bridge** only.

## Cluster (Ports + Memory)
| Agent | Port | Memory | Entrypoint |
|---|---:|---|---|
| hyper-brain-core | 3301 | redis | `hyper_brain_core.py` |
| mcp-bridge | 3302 | redis | `mcp_bridge.py` |
| focus-tracker | — | postgres | `focus_tracker.py` |
| morning-briefing | — | redis | `morning_briefing_ai.py` |

## Tool Registry (Static)

### hyper-brain-core
| Tool | Input | Output | Touches |
|---|---|---|---|
| `query_brain` | `query: string` | context text | vault notes |
| `update_brain` | `key: string`, `value: string` | ack | vault notes |

### mcp-bridge
| Tool | Input | Output | Touches |
|---|---|---|---|
| `bridge_call` | `tool: string`, `args: object` | tool result | agent network |

### focus-tracker
| Tool | Input | Output | Touches |
|---|---|---|---|
| `start_session` | `task: string`, `duration_mins: int` | `session_id` | `05-Focus-Sessions/` |
| `end_session` | `session_id: string` | score + log | `05-Focus-Sessions/` |

### morning-briefing
| Tool | Input | Output | Touches |
|---|---|---|---|
| `get_briefing` | `discord_id: string` | briefing text | `00-Inbox/Briefings/` |

## Next Improvements
- Link this from the Focus Command Center.

