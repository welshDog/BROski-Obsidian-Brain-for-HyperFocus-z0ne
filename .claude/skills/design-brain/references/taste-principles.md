# Taste Principles — Deep Aesthetic Reference

## The Core Idea

"Taste" is the difference between a UI that was assembled and one that was designed.
Most AI-generated UI is assembled — it applies correct syntax but has no point of view.
This skill gives you a point of view.

The goal isn't to be flashy. It's to be *intentional*.
Every decision — padding, colour, weight, timing — should have a reason.
When you can't explain why you made a choice, you're generating slop.

---

## Spacing System

Don't use arbitrary Tailwind spacing. Use this intentional scale:

```
Micro:    4px  (p-1)   — icon padding, badge gaps
Small:    8px  (p-2)   — inline element gaps
Base:     12px (p-3)   — default element padding  
Medium:   16px (p-4)   — component internal spacing
Large:    24px (p-6)   — section gaps, card padding
XL:       32px (p-8)   — major section breaks
2XL:      48px (p-12)  — hero breathing room
3XL:      64px (p-16)  — page-level vertical rhythm
```

**Rule:** A card's internal padding should match its visual weight.
Heavy content (lots of data) → tighter padding.
Hero/showpiece → generous padding.

Never mix arbitrary values (`p-5`, `p-7`) unless you have a specific optical reason.

---

## Colour Psychology for HyperCode

Each colour has a job. Respect it.

**#7c3aed (BROski purple)** — Authority, brand, primary actions
- Use for: primary CTAs, brand moments, subscription tier badges
- Never use for: backgrounds, error states, decorative accents
- Max usage: one element per screen section

**#f59e0b (BROski gold)** — Achievement, reward, warmth
- Use for: BROski$ tokens, XP gains, achievement unlocks, "win" moments
- Never use for: regular text, navigation, functional UI
- Pairs perfectly with a brief glow animation on earn events

**#22d3ee (cyan)** — Data, live, real-time
- Use for: live metrics, active states, terminal-style data, agent status
- Never use for: CTAs or brand moments — it's a data colour
- At full opacity it's harsh — use at 80% or less in text

**rgba(255,255,255,0.06) (border)** — Structure without noise
- Use for: card borders, dividers, input outlines
- Never use: solid white or grey borders — they're too loud on dark backgrounds
- For hover/focus: bump to rgba(255,255,255,0.15)

---

## Advanced Palette Usage

### Glassmorphism (use sparingly, only for overlays + modals)
```css
background: rgba(17, 17, 17, 0.8);
backdrop-filter: blur(12px);
border: 1px solid rgba(255, 255, 255, 0.08);
```

### Terminal aesthetic (for agent UI, code output, live feeds)
```
Background: #050505
Text:       #22d3ee at 90% opacity
Cursor:     #22d3ee, blinking 1s step-end infinite
Font:       JetBrains Mono, Fira Code, or system mono
Line height: 1.6 — monospace needs more breathing room
```

### Glow effects (only for emphasis moments — wins, live indicators)
```css
/* Token earn glow */
box-shadow: 0 0 20px rgba(245, 158, 11, 0.3);

/* Live indicator pulse */
box-shadow: 0 0 0 0 rgba(34, 211, 238, 0.4);
animation: pulse 2s cubic-bezier(0, 0, 0.2, 1) infinite;
```

---

## Typography Hierarchy

Always establish a clear type scale. Headings should feel like headings.

```
Display:  48-72px  font-bold  tracking-tight  line-height: 1.1
H1:       36-48px  font-bold  tracking-tight  line-height: 1.2
H2:       24-30px  font-semibold              line-height: 1.3
H3:       18-20px  font-semibold              line-height: 1.4
Body:     14-16px  font-normal                line-height: 1.6
Small:    12-13px  font-normal  text-muted    line-height: 1.5
Mono:     13-14px  font-mono                  line-height: 1.7
```

**For headings in HyperCode:** Mix font-mono for the "hacker" word and font-sans for the descriptor:
```jsx
<h1>
  <span className="font-mono text-cyan-400">HyperCode</span>
  {" "}
  <span className="font-bold">Mission Control</span>
</h1>
```

---

## Layout Principles

### Visual hierarchy over grid uniformity
Not everything should be the same size. Use scale to show importance.
- Primary metric: big, prominent
- Secondary info: medium
- Supporting detail: small, muted

### White space is structure
Empty space tells the eye where to rest. Don't fill it with decorative elements.
A well-spaced dark UI reads as premium. A dense dark UI reads as overwhelming.

### Focal point first
Every screen should have one thing the eye lands on first.
Then a clear path to the next thing.
If everything is equally prominent, nothing is.

### Asymmetry > symmetry for hero/showpiece
Symmetrical layouts are safe and forgettable.
Off-centre, weighted layouts feel intentional and confident.
Agent Mission Control should look like a cockpit, not a spreadsheet.

---

## The "One More Thing" Test

Before finishing any UI, ask: what's the one small change that would make this feel finished?

Common answers:
- The hover state is missing or wrong
- The loading skeleton looks like a grey bar instead of the actual layout
- The empty state says "No data" instead of something human and branded
- The mobile version is just the desktop version squished
- The success state has no visual celebration

Always address the "one more thing" before calling it done.
