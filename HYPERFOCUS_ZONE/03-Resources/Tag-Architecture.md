---
type: resource
title: Tag Architecture
tags:
  - meta
  - tags
  - system
created: 2026-05-31
updated: 2026-05-31
---

# 🏷️ Tag Architecture

> Consistent tags = smart Dataview queries = zero manual organizing.
> Tag first, file later. Let the queries do the sorting.

---

## 📂 Project Tags

| Tag | When to use |
|---|---|
| `#project/hypercode` | Anything HyperCode-V2.4 |
| `#project/course` | Hyper-Vibe-Coding-Course |
| `#project/broskipets` | BROskiPets LLM-dNFT |
| `#project/agents-ide` | HYPER Agents IDE |
| `#project/showcase` | Showcase website |
| `#project/brain` | This Obsidian Brain vault |
| `#project/sdk` | HyperAgent SDK |

---

## 🏷️ Type Tags

| Tag | When to use |
|---|---|
| `#type/session` | Focus session or coding session log |
| `#type/decision` | A decision made (with reasoning) |
| `#type/blocker` | Something blocking progress |
| `#type/win` | Something shipped or achieved |
| `#type/idea` | Raw idea, not actionable yet |
| `#type/bug` | Bug found or fixed |
| `#type/brain-dump` | Quick unstructured capture |

---

## 🔋 Energy Tags

| Tag | When to use |
|---|---|
| `#energy/high` | Hyperfocus material — complex, creative |
| `#energy/medium` | Normal tasks — PRs, docs, fixes |
| `#energy/low` | Low-effort — reviews, admin, cleanup |

> 💡 **ADHD pro tip:** Tag tasks with energy level, then on foggy brain days filter for `#energy/low` only.

---

## 📊 Status Tags

| Tag | When to use |
|---|---|
| `#status/now` | Actively working on |
| `#status/next` | Queued for today/tomorrow |
| `#status/blocked` | Waiting on something |
| `#status/done` | Complete — move to Archive |
| `#status/parked` | Intentionally paused |

---

## 🗓️ Time Tags

| Tag | When to use |
|---|---|
| `#review/weekly` | Appears in weekly review |
| `#review/monthly` | Appears in monthly review |
| `#daily` | Daily note content |

---

## 📐 Example Usage

A note about fixing the Stripe webhook:

```yaml
---
tags:
  - project/course
  - type/bug
  - energy/medium
  - status/done
---
```

A brain dump about a new feature idea:

```yaml
---
tags:
  - project/brain
  - type/idea
  - energy/high
  - status/parked
---
```

---

## 🔍 Dataview Queries Using Tags

### All blockers across projects
```dataview
LIST
FROM #type/blocker AND -#status/done
SORT file.mtime DESC
```

### Low-energy tasks for foggy days
```dataview
TASK
FROM #energy/low AND -#status/done
SORT file.mtime DESC
```

### All wins (dopamine boost)
```dataview
LIST
FROM #type/win
SORT file.mtime DESC
LIMIT 10
```

---

> 🧠 Don't overthink tags. Use what feels right. You can always re-tag later.
