# Impeccable — UI Audit Reference

## The Audit Philosophy

"Impeccable" means finding the gap between what a UI looks like and what it *should* look like.
It's a systematic pass — not vibes-based, but not cold either.

The goal isn't to nitpick. It's to find the few things that are meaningfully degrading the experience
and fix those first. A 3-issue audit that actually gets actioned beats a 20-issue audit that overwhelms.

---

## Scoring Rubric (0–10)

| Score | Meaning |
|---|---|
| 9–10 | Production-ready. Elevation moves only. |
| 7–8 | Good bones, needs polish in specific areas. |
| 5–6 | Functional but generic. Multiple issues hold it back. |
| 3–4 | Significant problems. Needs rework, not tweaks. |
| 1–2 | Slop. Structural redesign required. |

Always be honest with the score. A 4 is not a 6.
Never give a 9+ unless it genuinely deserves it.

---

## The Six Audit Categories

Grade each category. Surface the worst ones as Critical Fixes.

### 1. Layout (max 10)

Check:
- Is there a clear visual hierarchy? (primary → secondary → detail)
- Does the grid/flex structure create logical groupings?
- Is there one focal point per screen section?
- Does the layout breathe? Or is it claustrophobic?
- Does it survive a "squint test"? (blur your eyes — structure should still read)

Common issues:
- Everything the same size = no hierarchy
- Too many equal columns = no focal point
- Padding inconsistent with content weight
- Nested cards (cards inside cards) with identical styling

### 2. Typography (max 10)

Check:
- Is there a clear type scale? (at least 3 distinct sizes)
- Are headings actually heading-like in weight and size?
- Is line-height correct? (body: 1.5–1.7, headings: 1.1–1.3, mono: 1.6–1.8)
- Is text colour correct? (body: ~#e8e8e8, muted: ~#888, not white, not grey-400)
- Is font choice appropriate? (mono for data/code/hacker, sans for body)

Common issues:
- Body text too light or too dark
- Line height too tight on paragraphs
- Heading same weight as body
- `text-sm text-gray-400` used as body text (barely readable on dark bg)

### 3. Colour (max 10)

Check:
- Does the palette have a clear hierarchy? (background → surface → accent)
- Are accents used sparingly? (accent colour on >30% of elements = not accent anymore)
- Is contrast sufficient? (4.5:1 for body, 3:1 for large text — WCAG AA minimum)
- Is it using the custom palette or defaulting to Tailwind generics?
- Are borders using rgba, not solid colours?

Common issues:
- Default Tailwind purple/blue instead of custom palette
- Accent colour on too many elements simultaneously
- Border colours too opaque / too visible
- Text/background pairs that fail contrast check

### 4. Spacing (max 10)

Check:
- Is spacing consistent with the 4/8/12/16/24/32/48/64 scale?
- Does vertical rhythm feel regular? Or bumpy?
- Does section-level spacing create clear breaks?
- Are similar elements spaced the same way?

Common issues:
- `p-5` everywhere (off the 4px grid)
- Card padding doesn't match the content's visual weight
- Section breaks too small (sections blur together)
- List items need more vertical gap

### 5. Motion (max 10)

Check:
- Are transitions present on interactive elements?
- Is the easing appropriate? (spring for enter, ease-out for exit)
- Are durations proportional to distance/scale of change?
- Is `transition-all` being used? (banned)
- Does animation respect `prefers-reduced-motion`?

Common issues:
- No hover/focus states
- `transition-all duration-300` on everything
- Scale too large on hover (>1.05)
- Missing exit animations
- Entrance animations on non-interactive elements (gratuitous)

### 6. Accessibility (max 10)

Check:
- Do all interactive elements have focus styles?
- Are focus styles designed, not removed?
- Is the click target sufficient? (44×44px minimum for touch)
- Are icons without text given aria-labels?
- Is colour alone being used to convey information?

Common issues:
- `focus:outline-none` with no replacement
- Icon buttons with no accessible label
- Small click targets (especially mobile)
- Status shown only by colour (e.g. red/green with no icon/text)

---

## HyperCode-Specific Drift Patterns

These are the patterns most likely to appear in this codebase over time:

### Dashboard drift
- Starts clean, gradually accumulates `text-sm text-gray-500` everywhere
- Fix: audit every muted text and give it a purpose

### Component copy-paste slop
- Same card component used for 5 different things → loses personality
- Fix: give each surface type its own visual treatment

### Tailwind colour regression
- Developer uses `text-purple-500` instead of the custom accent
- Fix: purge generic Tailwind colour classes, enforce custom palette in tailwind.config

### BROski$ UI undercelebration
- Token earns shown as a plain number with no animation
- Fix: every BROski$ event deserves a micro-celebration (see emil-patterns.md)

### Mobile afterthought
- Desktop looks great, mobile is squished and overcrowded
- Fix: mobile-first, then enhance for desktop

---

## Prioritising Fixes

Not all issues are equal. Prioritise in this order:

1. **Contrast failures** — Accessibility, may be illegal in some contexts
2. **No interactive states** — Hover/focus/active — makes the UI feel broken
3. **Typography collapse** — No visual hierarchy = impossible to scan (critical for ND users)
4. **Spacing inconsistency** — Destroys the sense of intentionality
5. **Colour palette drift** — Undermines brand identity
6. **Motion issues** — Polish, usually non-blocking

---

## Audit Output Template

```
## 🔍 Audit Score: X/10

### Category Breakdown
| Category | Score | Key issue |
|---|---|---|
| Layout | /10 | ... |
| Typography | /10 | ... |
| Colour | /10 | ... |
| Spacing | /10 | ... |
| Motion | /10 | ... |
| Accessibility | /10 | ... |

## 🚨 Critical Fixes (top 3 max)

### 1. [Issue name]
**Problem:** [What's wrong and why it matters]
**Fix:**
```code snippet```

### 2. [Issue name]
...

## ⚠️ Polish Wins (top 4 max)

- **[Issue]:** [One-line fix]
- ...

## ✅ What's Working

- [3 genuine positives]

## 🔮 Elevation Moves (only if score ≥ 7)

- [What would make this memorable vs just good]
```
