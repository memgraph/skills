---
name: memgraph-brand-ui
description: Generate apps, demos, dashboards, diagrams, landing pages, and any visual output that looks like it belongs in the Memgraph product family. Use whenever producing UI, visual artifacts (Mermaid, SVGs, charts), Lab-style admin tools, internal dashboards, feature splash pages, or embeddable widgets for Memgraph engineers.
compatibility: Any frontend framework (React, Vue, Svelte, plain HTML/CSS, Tailwind, etc.)
metadata:
  author: memgraph
  version: "0.0.1"
---

# Memgraph Brand Skill

You are designing for **Memgraph** — an in-memory graph database. The product surface is workbench-dense, neutral-first, technical. Engineers, not consumers.

## When to Use

- Generating any UI screen, page, or layout for a Memgraph product
- Building frontend components (buttons, cards, forms, dashboards, etc.)
- Creating design tokens, theme files, or CSS variables
- Generating diagrams (Mermaid, PlantUML, Graphviz, draw.io, etc.)
- Creating flowcharts, architecture diagrams, or sequence diagrams
- Building data visualizations, charts, or graphs (D3, Chart.js, etc.)
- Producing SVGs, icons, or illustrative graphics
- Designing presentation slides or visual documentation
- Reviewing or fixing any visual output for brand compliance
- Lab-style admin tools, internal dashboards, feature splash pages, embeddable widgets

## The Two Rules Everything Hangs Off

1. **Neutral first, orange second.** Whites and grays do 90%+ of the work. Orange is an accent, not a theme.
2. **Restraint over decoration.** No gradient backgrounds. No invented colors. No drop shadows on everything. No emoji. No rounded-pill buttons. No icon soup.

If a choice fights either rule, it's wrong.

---

## Tokens (use these literally — do not invent variants)

### Color

```
--brand-black:   #231F20   /* primary text, strong borders, dark surfaces */
--brand-orange:  #FB6E00   /* accent only — primary buttons, active states, links */
--orange-tint:   #FFF4EB   /* soft orange badge bg */

--gray-1:   #646265        /* secondary text */
--gray-2:   #857F87        /* muted text */
--gray-3:   #BAB8BB        /* placeholder, disabled */
--gray-4:   #E6E6E6        /* hairline borders, dividers */
--gray-5:   #F9F9F9        /* canvas/zebra/hover bg — NEVER on cards */
--white:    #FFFFFF        /* default surface, including all cards */

--success:  #19AF66
--error:    #DC2223
--warning:  #FFC500        /* brand yellow, used semantically */
--purple:   #720096        /* marketing accent only — not in product chrome */
```

**Color usage:**
- Backgrounds: `#FFFFFF` (default surface, all cards), `#F9F9F9` (canvas / page bg / hover state). Never anything else.
- Text: `#231F20` primary, `#646265` secondary, `#857F87` muted. Three steps total.
- Borders: `#E6E6E6` hairlines, `#231F20` for emphasized outline buttons. **Never use `#FB6E00` as a border color.**
- Orange budget: ~10% of pixels. Primary CTA, active nav indicator, focus ring, the wordmark. That's it.
- Yellow / red / purple appear **only semantically** (warning / error / marketing-illustration accent). Not as decoration.

### The Brand Gradient — Handle With Care

A `#FFC500 → #DC2223 → #720096` gradient exists in the brand kit. It is **never a background fill on a UI surface**. Acceptable uses, max one per page:
- A thin 2–4px decorative bar at the top of a marketing hero
- A small splash mark behind a logo or hero number
- A single icon-tile gradient on a landing page

If you find yourself painting a card, button, header, or section bg with the gradient, stop. Use orange or neutral instead.

### Type

- **UI everything: `Inter Tight`.** Headings, body, buttons, labels, nav, tables — all Inter Tight.
- **Code only: `Ubuntu Mono`.** Cypher queries, code blocks, inline code, monospace numbers in dense tables.
- Do not introduce Roboto, Encode Sans, system-ui, Inter, or anything else.

Weight scale (use these — do not freestyle):
```
Body / paragraph:  400
UI labels, nav:    500
Buttons, H4–H6:    600
H1–H3:             700  (800 only for marketing display)
```

Size scale (px / line-height):
```
Display H1:  48 / 56    or 64 / 72 for marketing hero
H2:          32 / 40
H3:          24 / 32
H4:          20 / 28
H5 / strong: 16 / 20
Body:        16 / 24
Small:       13 / 20    (default for dense UI: chips, tags, table cells)
Micro:       11 / 12    (eyebrow labels, table column heads — uppercase, +0.06em tracking)
Code:        13 / 20    Ubuntu Mono
```

Letter-spacing: `-0.01em` on display headings, `+0.04em` on uppercase button labels and eyebrows, default elsewhere.

### Spacing — Strict 4px Grid

`0, 4, 8, 12, 16, 24, 32, 40, 48, 64, 80`. Nothing in between. Component padding is usually 8/12/16. Card padding 16/24. Section gaps 40/64.

### Radii — Strict 2–8px

```
2px   tiny tags, swatches, micro-badges
4px   default — buttons, inputs, cards, dropdowns, modals
8px   large containers, marketing cards, hero tiles
999px ONLY avatars, status dots, loading spinners
```
Never 12, 16, 24. Never `border-radius: 9999px` on buttons or chips.

### Shadows

```
--shadow-card:    0 2px 10px 0 rgba(0,0,0,0.10);   /* card lift */
--shadow-button:  2px 2px 8px 0 rgba(0,0,0,0.24);  /* primary button — note: asymmetric */
--shadow-elev:    0 0 4px 0 rgba(0,0,0,0.25);      /* outlined button */
--shadow-drop:    0 4px 12px 0 rgba(35,31,32,0.16);/* popovers, dropdowns */
--shadow-focus:   0 0 0 3px rgba(251,110,0,0.24);  /* keyboard focus */
```
No inner shadows. No glow. Stack at most one shadow per element.

---

## Component Cheat Sheet

### Buttons

```html
<!-- Primary: orange fill, white text, asymmetric shadow -->
<button style="background:#FB6E00;color:#fff;border:0;border-radius:4px;
  padding:8px 16px;font:600 16px/20px 'Inter Tight';letter-spacing:.04em;
  box-shadow:2px 2px 8px 0 rgba(0,0,0,.24);cursor:pointer">Run query</button>

<!-- Secondary: white fill, black border. NEVER orange border. -->
<button style="background:#fff;color:#231F20;border:1px solid #231F20;
  border-radius:4px;padding:8px 16px;font:600 16px/20px 'Inter Tight';
  letter-spacing:.04em">Disconnect</button>

<!-- Ghost: transparent, hover paints #F9F9F9 -->
<button style="background:transparent;color:#231F20;border:0;
  border-radius:4px;padding:8px 16px;font:600 16px/20px 'Inter Tight'">Cancel</button>
```
Hover: primary darkens to `#E36300`, secondary fills to `#F9F9F9`. Press: subtle scale `0.98` or shadow flatten — never color shrink.

### Cards

White background. **Either** a 1px `#E6E6E6` border **or** the card shadow — rarely both. 4px radius. 16/24 inner padding.

```html
<div style="background:#fff;border:1px solid #E6E6E6;border-radius:4px;
  padding:16px 20px;font-family:'Inter Tight'">
  <div style="font:600 16px/20px 'Inter Tight';color:#231F20">Schema overview</div>
  <p style="font:400 13px/20px 'Inter Tight';color:#646265;margin:4px 0 0">
    12 node labels · 28 edge types · 3 indexes
  </p>
</div>
```

### Inputs

1px `#E6E6E6` border, 4px radius, 8/12 padding, 16/20 Inter Tight 400, placeholder `#BAB8BB`. Focus: border `#231F20` + 3px orange focus shadow.

### Tags / Chips

```html
<span style="display:inline-block;padding:3px 8px;border-radius:2px;
  background:#FFF4EB;color:#FB6E00;
  font:600 11px/12px 'Inter Tight';letter-spacing:.06em;text-transform:uppercase">
  TRANSACTIONAL
</span>
```

### Layout Patterns Memgraph Uses

- **App shell:** dark sidenav (`#231F20`, 196px wide) + top status bar (40–64px) + main canvas. Active nav item: 3px left orange bar + slightly lighter row bg.
- **Status bars:** sticky, full-bleed, dense. Connection pill, then stat cluster (Edges · Indexes · Triggers · Memory), then help/notifications, then disconnect button.
- **Tables:** `#F9F9F9` zebra at most. Hairline `#E6E6E6` rows. Numeric columns in Ubuntu Mono.
- **Marketing hero:** big Inter Tight heading (48–80px, 700–800), short subhead in `#646265`, one primary orange CTA, one ghost link. White or `#F9F9F9` background. The gradient (if any) is a 4px top-of-page rule or a small mark — not the bg.

---

## Voice & Content

- **Second person, imperative.** "Run query", "Connect to instance", "Disconnect", "Add a trigger". Not "Initiate connection".
- **Sentence case** for buttons, menu items, tabs. **Title Case** only for proper-noun feature names (Run History, Graph Style Script, Query Collections).
- **UPPERCASE** only for micro-eyebrows (≤13px, +0.06em tracking).
- **No exclamation marks. No emoji. No marketing fluff inside product UI.**
- Numbers: thousands separators (`2,128`), units adjacent (`517.08 MB`).
- Jargon is welcome and expected: Cypher, trigger, index, edge, node, schema, transaction, multitenancy.

---

## Do / Don't

| Do | Don't |
|---|---|
| White cards on `#F9F9F9` page bg | Light-gray cards on white |
| Orange for primary CTA only | Orange section backgrounds, orange borders, orange dividers |
| Inter Tight everywhere; Ubuntu Mono for code | System UI, Inter, Roboto, "modern sans" |
| 4px radius default | 12px, 16px, fully-rounded buttons |
| One shadow per element | Layered shadows + glow |
| Three text colors: #231F20, #646265, #857F87 | New gray tones, blue-tinted grays |
| Gradient: thin decorative bar or single mark, max once per page | Gradient backgrounds, gradient buttons, gradient cards |
| Hairline `#E6E6E6` borders | Thick borders, double borders, colored left-stripe cards |
| Custom Memgraph icons (24×24, filled silhouette) | Lucide / Material / Heroicons / emoji as icons |

---

## Starter HTML

Always begin with these tokens loaded. Inter Tight from Google Fonts is acceptable when the brand variable font isn't available.

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Memgraph — …</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;500;600;700;800&family=Ubuntu+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
  :root {
    --brand-black:#231F20; --brand-orange:#FB6E00; --orange-tint:#FFF4EB;
    --gray-1:#646265; --gray-2:#857F87; --gray-3:#BAB8BB;
    --gray-4:#E6E6E6; --gray-5:#F9F9F9; --white:#FFFFFF;
    --success:#19AF66; --error:#DC2223; --warning:#FFC500;
    --r-sm:2px; --r-md:4px; --r-lg:8px;
    --shadow-card:0 2px 10px 0 rgba(0,0,0,.10);
    --shadow-button:2px 2px 8px 0 rgba(0,0,0,.24);
    --shadow-elev:0 0 4px 0 rgba(0,0,0,.25);
    --shadow-focus:0 0 0 3px rgba(251,110,0,.24);
  }
  *,*::before,*::after { box-sizing:border-box; }
  html,body { margin:0; background:var(--gray-5); color:var(--brand-black);
    font:400 16px/24px 'Inter Tight', system-ui, sans-serif; }
  code, pre, .mono { font-family:'Ubuntu Mono', Consolas, monospace; }
  h1,h2,h3,h4,h5,h6 { font-family:'Inter Tight'; color:var(--brand-black);
    margin:0; letter-spacing:-0.01em; }
  h1 { font-size:48px; line-height:56px; font-weight:700; }
  h2 { font-size:32px; line-height:40px; font-weight:700; }
  h3 { font-size:24px; line-height:32px; font-weight:700; }
  h4 { font-size:20px; line-height:28px; font-weight:600; }
  h5 { font-size:16px; line-height:20px; font-weight:600; }
  h6 { font-size:13px; line-height:16px; font-weight:600;
       text-transform:uppercase; letter-spacing:.06em; color:var(--gray-1); }
  ::selection { background:var(--orange-tint); color:var(--brand-black); }
</style>
</head>
<body>
  <!-- design here, on a #F9F9F9 canvas, with #FFFFFF cards -->
</body>
</html>
```

---

## Process — How to Use This Skill

1. **Confirm the surface.** Ask: is this product chrome (Lab-style admin), an internal dashboard, a diagram, or marketing? Each pulls different presets — product chrome = densest, marketing = biggest type, allow one decorative gradient mark, diagrams = token colors only.
2. **Sketch in tokens.** Reach for the variables above before writing any rule. If a value isn't in the token list, you don't need it.
3. **Audit the orange.** Count orange surfaces on screen. More than one prominent orange element per viewport? Cut.
4. **Audit the radii.** Anything outside {2, 4, 8, 999} gets normalized.
5. **Audit the fonts.** One font for UI (Inter Tight), one for code (Ubuntu Mono). Anything else is a bug.
6. **Read the copy out loud.** If it sounds like a marketing brochure inside the product, rewrite it shorter and more imperative.

When in doubt: more white space, fewer colors, smaller radii, smaller orange.
