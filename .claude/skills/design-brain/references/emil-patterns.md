# Emil Kowalski Micro-Interaction Patterns

## The Philosophy

Emil's approach: interactions should feel *physical*.
A button press should feel like pressing a button. A menu opening should feel like a panel sliding out from somewhere real.

The mistake most UIs make: they animate properties that change layout (width, height, top, left).
This causes reflow and jank. Emil's rule: **only animate transform and opacity**.

Everything else is a cheat: clip-path for reveals, scale for size changes, translateY for position.

---

## Core Animation Rules

### The Two Properties
```css
/* ALWAYS hardware-accelerated — use freely */
transform: translateX() translateY() scale() rotate();
opacity: 0 → 1;

/* NEVER animate — causes layout thrash */
width, height, top, left, right, bottom
padding, margin, border-width
```

### The Easing Library

```css
/* Spring — for entrances, feels alive */
--ease-spring: cubic-bezier(0.16, 1, 0.3, 1);

/* Smooth out — for exits */
--ease-out: cubic-bezier(0, 0, 0.2, 1);

/* Snappy — for micro-interactions (buttons, toggles) */
--ease-snappy: cubic-bezier(0.34, 1.56, 0.64, 1);  /* slight overshoot */

/* Linear — for continuous animations only (loaders, live indicators) */
--ease-linear: linear;
```

### Duration Scale

```
Instant:   0ms    — no animation (low motion preference)
Micro:     100ms  — hover colour change, focus ring
Fast:      150ms  — button press, toggle
Normal:    200ms  — tooltip, dropdown appear
Medium:    300ms  — modal, drawer slide in
Slow:      500ms  — page entrance, hero animation
Very slow: 800ms+ — only for deliberate theatrical moments
```

---

## Component Recipes

### Button — Press feel
```tsx
// The key: scaleDown on mousedown, spring back on mouseup
// NOT a hover scale up (that's amateur)
<button
  className="
    bg-violet-600 text-white px-4 py-2 rounded-md
    transition-transform duration-150
    hover:brightness-110
    active:scale-[0.97]
    focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-500
  "
  style={{ transition: 'transform 150ms cubic-bezier(0.34, 1.56, 0.64, 1)' }}
>
  Click me
</button>
```

### Card — Lift on hover
```tsx
// Lift = translateY UP (negative) + subtle shadow change
// NOT scale up — scale up inflates the card and breaks layout rhythm
<div
  className="
    bg-[#111] border border-white/6 rounded-lg p-6
    transition-all duration-200
    hover:-translate-y-0.5
    hover:border-white/10
    hover:shadow-[0_8px_30px_rgba(0,0,0,0.4)]
  "
>
```

### Dropdown / Menu — Slide + fade from source
```tsx
// Appear from just above (translateY: -4px → 0) + fade in
// The origin of the animation should be near where the trigger is
<motion.div
  initial={{ opacity: 0, y: -4, scale: 0.97 }}
  animate={{ opacity: 1, y: 0, scale: 1 }}
  exit={{ opacity: 0, y: -4, scale: 0.97 }}
  transition={{ duration: 0.15, ease: [0.16, 1, 0.3, 1] }}
>
```

### Modal — Centre entrance
```tsx
// Scale from 0.95 + fade — feels like it materialises
// NOT slide from edge — that's a drawer, not a modal
<motion.div
  initial={{ opacity: 0, scale: 0.95 }}
  animate={{ opacity: 1, scale: 1 }}
  exit={{ opacity: 0, scale: 0.95 }}
  transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
>
```

### Drawer — Slide from edge
```tsx
// translateX from off-screen — but start close, not fully off screen
// Starting from 100% feels sluggish. Start from 30px off.
<motion.div
  initial={{ opacity: 0, x: 30 }}
  animate={{ opacity: 1, x: 0 }}
  exit={{ opacity: 0, x: 30 }}
  transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
>
```

### Loading Skeleton — Reveal, not pulse
```tsx
// Pulse skeletons feel old. Use a shimmer sweep instead.
// Or better: match the exact shape of the content that's loading
<div className="
  bg-white/5 rounded
  overflow-hidden relative
  before:absolute before:inset-0
  before:bg-gradient-to-r before:from-transparent before:via-white/8 before:to-transparent
  before:animate-[shimmer_1.5s_infinite]
" />
```

### Token Earn / Achievement — Celebration moment
```tsx
// BROski$ awarded: burst of colour + number counting up
// This is one of the few places to break the restraint rules
const EarnEvent = ({ amount }) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.5, y: 10 }}
    animate={{ opacity: 1, scale: 1, y: 0 }}
    exit={{ opacity: 0, scale: 0.8, y: -20 }}
    transition={{ type: "spring", stiffness: 400, damping: 17 }}
    className="text-amber-400 font-mono font-bold text-lg"
  >
    +{amount} BROski$
  </motion.div>
)
```

---

## Stagger Pattern (for lists, grids, dashboards)

```tsx
// Stagger children entrance — each delays by 50ms from the previous
// Keeps the UI feeling alive without being distracting
const container = {
  hidden: {},
  show: {
    transition: { staggerChildren: 0.05 }
  }
}

const item = {
  hidden: { opacity: 0, y: 8 },
  show: { 
    opacity: 1, 
    y: 0,
    transition: { duration: 0.3, ease: [0.16, 1, 0.3, 1] }
  }
}
```

---

## Focus & Accessibility Rules

Emil is strict about focus states — they're not optional.

```tsx
// Never just remove focus ring. Replace it with something designed.
// Tailwind:
focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-violet-500/70 focus-visible:ring-offset-2 focus-visible:ring-offset-[#0a0a0a]
```

**Reduced motion — always respect:**
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```
Or in Framer Motion: check `useReducedMotion()` and conditionally remove animations.

---

## Common Mistakes to Avoid

| Mistake | Fix |
|---|---|
| Hover scale >1.03 on cards | Use translateY(-2px) lift instead |
| `transition-all` | List specific properties |
| Same easing for all animations | Match easing to the type (spring for enter, ease-out for exit) |
| No exit animation | Always define exit to match the enter in reverse |
| Animating `height: 0 → auto` | Use `scaleY` or `Framer Motion` layout animations |
| Animate on mount unconditionally | Respect `prefers-reduced-motion` |
| Delay on hover interactions | Max 50ms delay, never >100ms on hover |
