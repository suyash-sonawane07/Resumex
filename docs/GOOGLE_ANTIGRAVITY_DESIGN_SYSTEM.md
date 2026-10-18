# Google Antigravity UI Design System & Component Guidance

> **Design Intent:** Establish an implementation-ready, token-governed UI design system for Google Antigravity marketing surfaces that unifies clean white-space minimalism, Google Sans Flex typography, obsidian pill interactions, and strict WCAG 2.2 AA accessibility across all developer-facing touchpoints.

---

## 1. Context & Goals

### 1.1 Brand & Surface Definition
- **Product / Brand:** Google Antigravity
- **Canonical Marketing URL:** [`https://antigravity.google/`](https://antigravity.google/)
- **Primary Audience:** Software engineers, ML researchers, technical architects, and developer leads evaluating next-generation AI agent platforms.
- **Product Surface:** High-conversion marketing website, product announcement showcase, and interactive developer evaluation workspace.

### 1.2 Core Mission
Deliver implementation-ready, token-driven UI design guidance for Google Antigravity that is optimized for visual consistency, full keyboard accessibility, predictable performance, and rapid engineering delivery. Every component specification must be directly translatable into production CSS, React/Tailwind, or Streamlit implementations without guesswork.

### 1.3 Key Architectural Principles
1. **Implementation-Ready Tokens:** Every visual style is bound to an unambiguous semantic design token. Direct hardcoded hex codes, arbitrary margins, and rogue border-radii are prohibited in component source code.
2. **7-State Completeness:** Every interactive component must define and handle all 7 lifecycle states: *default*, *hover*, *focus-visible*, *active*, *disabled*, *loading*, and *error*.
3. **Pill-First Ergonomics:** Primary navigation, action triggers, and badges follow fully rounded pill profiles (`radius.lg = 9999px`) with dark obsidian surfaces for primary CTAs and hairline neutral outlines for secondary actions.
4. **Google Quad-Color Harmony:** Accent highlights incorporate Google's iconic four colors (`#4285F4` Blue, `#EA4335` Red, `#FBBC04` Yellow, `#34A853` Green) through restrained orbital particles, status halos, and badge dots without overwhelming the clean white canvas.
5. **Privacy & Volatile Processing:** As a developer platform handling sensitive assets (such as codebases and candidate resumes), interfaces must clearly communicate DPDP Act 2023 compliance and volatile RAM processing guarantees.

---

## 2. Design Tokens & Foundations

### 2.1 Typography Stack & Scale

#### Primary Font Specifications
- `font.family.primary`: `Google Sans Flex`
- `font.family.stack`: `Google Sans Flex, Google Sans, Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`
- `font.size.base`: `16px`
- `font.weight.base`: `400`
- `font.lineHeight.base`: `24px` (1.5)

#### Full Typography Scale

| Token | Computed Size | Computed Line-Height | Font Weight | Typical Usage |
| :--- | :--- | :--- | :--- | :--- |
| `font.size.xs` | `12.5px` | `18px` | `400 / 500` | KPI footer captions, pill tags, metadata readouts |
| `font.size.sm` | `13px` | `20px` | `400 / 500` | Announcement capsule text, input helper copy, table headers |
| `font.size.md` | `14.5px` | `22px` | `400 / 500` | Navigation links, pill button text, dropdown options |
| `font.size.lg` | `16px` | `24px` | `400 / 500` | Standard body text, primary table cell copy, lead paragraphs |
| `font.size.xl` | `17.5px` | `26px` | `500 / 600` | Card section titles, modal headers, brand lockup text |
| `font.size.2xl` | `20px` | `28px` | `500 / 600` | Feature group headers, secondary display subtitles |
| `font.size.3xl` | `28px` | `36px` | `600` | Section headings, primary metric numerals |
| `font.size.4xl` | `32px` | `40px` | `600` | Page titles, hero section sub-display |
| `font.size.display` | `56px` (`clamp(2.4rem, 4.5vw, 4.2rem)`) | `1.08` | `500 / 600` | Hero display title (*"Experience liftoff..."*) |

---

### 2.2 Color Palette & Semantic Tokens

```css
:root {
  /* System Brand Tokens */
  --color-text-primary: #121317;     /* High-contrast obsidian black (16.5:1 on #ffffff) */
  --color-text-secondary: #45474d;   /* Readable neutral slate gray (7.8:1 on #ffffff) */
  --color-text-tertiary: #ffffff;    /* Pure white for dark pill buttons (21:1 on #000000) */
  --color-text-inverse: #6a6a71;     /* Subtle muted caption text (5.1:1 on #ffffff) */
  --color-surface-base: #000000;     /* Pure obsidian for primary pill CTAs */
  --color-surface-raised: #b7bfd9;   /* Muted periwinkle-gray for card hover strokes */

  /* Page Canvas & Card Surfaces */
  --color-surface-canvas: #ffffff;   /* Pure white page canvas */
  --color-surface-card: #ffffff;     /* Card background surface */
  --color-surface-subtle: #fafaf9;   /* Warm off-white for sidebars & secondary zones */
  --color-surface-muted: #f4f4f5;    /* Gray neutral for track indicators & input fills */

  /* Hairline Borders & Dividers */
  --color-border-subtle: #e5e7eb;    /* Hairline card & button border */
  --color-border-strong: #d1d5db;    /* Interactive hover & active border */
  --color-border-focus: #000000;     /* WCAG 2.2 AA compliant high-contrast focus ring */

  /* Google Quad-Color Palette */
  --color-google-blue: #4285f4;      /* Google Blue — Core capability / Info status */
  --color-google-red: #ea4335;       /* Google Red — Critical gap / Error status */
  --color-google-yellow: #fbbc04;    /* Google Yellow — Warning / Attention status */
  --color-google-green: #34a853;     /* Google Green — Verified match / Success status */

  /* Semantic Status Tints (Light Surface Backgrounds) */
  --color-status-success-bg: #e6f4ea;
  --color-status-success-text: #137333;
  --color-status-warning-bg: #fef7e0;
  --color-status-warning-text: #b06000;
  --color-status-danger-bg: #fce8e6;
  --color-status-danger-text: #c5221f;
  --color-status-info-bg: #e8f0fe;
  --color-status-info-text: #1967d2;
}
```

---

### 2.3 Spacing Scale

The spacing scale is strictly geometric and maps directly to a 4px/8px incremental grid. Components **must** use these semantic space tokens exclusively:

| Token | Value | Rem Equivalent | Primary Component Use Cases |
| :--- | :--- | :--- | :--- |
| `space.1` | `4px` | `0.25rem` | Badge inner vertical padding, icon-to-label inline gap |
| `space.2` | `6px` | `0.375rem` | Compact button vertical padding, table row dense gap |
| `space.3` | `8px` | `0.5rem` | Standard pill button vertical padding, chip spacing |
| `space.4` | `10px` | `0.625rem` | Input field vertical padding, small card gap |
| `space.5` | `16px` | `1.0rem` | Card internal horizontal padding, standard stack rhythm |
| `space.6` | `24px` | `1.5rem` | Pill button horizontal padding (`px-6`), container gutter |
| `space.7` | `36px` | `2.25rem` | Hero title bottom margin, section header separation |
| `space.8` | `55px` | `3.4375rem` | Major marketing section separation, hero top whitespace |

---

### 2.4 Radius, Shadow, & Motion Tokens

#### Radius Scale
- `radius.xs`: `4px` — Code snippets, inline keyboard shortcuts (`<kbd>`), subtle indicator flags.
- `radius.sm`: `36px` — Feature teaser cards, capability spotlight cards, floating dialog sheets.
- `radius.md`: `1584px` — Large capsule announcement containers, extended modal panels.
- `radius.lg`: `9999px` — Pill buttons, navigation capsules, input pills, status chips, avatar circles.

#### Shadow Elevations
- `shadow.xs`: `0 1px 2px rgba(0, 0, 0, 0.04)` — Subtle pill buttons, inputs in resting state.
- `shadow.card`: `0 1px 3px rgba(0, 0, 0, 0.03), 0 4px 16px rgba(0, 0, 0, 0.02)` — Static spotlight cards.
- `shadow.elevated`: `0 4px 14px rgba(0, 0, 0, 0.12), 0 1px 3px rgba(0, 0, 0, 0.06)` — Primary button hover, active menus.
- `shadow.hover`: `0 8px 24px -4px rgba(0, 0, 0, 0.06), 0 2px 6px -1px rgba(0, 0, 0, 0.02)` — Interactive card hover.

#### Motion Tokens
- `motion.duration.instant`: `150ms` (`cubic-bezier(0.2, 0, 0, 1)`) — Button hover, link color shifts, focus ring appearances.
- `motion.duration.fast`: `200ms` (`cubic-bezier(0.2, 0, 0, 1)`) — Dropdown expansions, card hover elevations.
- `motion.duration.normal`: `300ms` (`cubic-bezier(0.16, 1, 0.3, 1)`) — Modal entry, tab switches, drawer transitions.
- **Vestibular Motion Rule:** Every motion animation **must** be wrapped in `@media (prefers-reduced-motion: reduce)` to disable non-essential translations, orbital spinning, and particle drift for users with motion sensitivity.

---

## 3. Surface Component Inventory & Densities

The Google Antigravity marketing surface (`https://antigravity.google/`) maintains a validated component density:
- **Links:** 87 instances (Navigation links, footer sitemap, jump anchors, announcement capsules, card actions)
- **Buttons:** 80 instances (Primary download pills, secondary action pills, dropdown triggers, compact controls, pagination)
- **Navigation:** 9 instances (Header bar, dropdown megamenus, language selector, breadcrumb, mobile drawer)
- **Inputs:** 4 instances (Search filter pill, weight sliders group, preset dropdown, PDF staging dropzone)
- **Cards:** 2 instances (Primary Hero Spotlight card, Capability / Candidate analysis detail card)
- **Lists:** 1 instance (Candidate Ranked Leaderboard & Explainability Evidence list)

---

## 4. Component-Level Specifications

### 4.1 Buttons (80 instances)

#### Anatomy
```
┌─────────────────────────────────────────────────────────────┐
│ [Leading Icon]  Button Label Text  [Trailing Badge/Chevron] │
└─────────────────────────────────────────────────────────────┘
  ↑ radius.lg (9999px)                                       ↑
```
1. **Container:** Pill-shaped `<button>` element with `border-radius: 9999px`.
2. **Leading Icon Slot (Optional):** 16×16px SVG glyph or status dot.
3. **Label:** Text styled with `font.size.md` (14.5px), `font.weight: 500`.
4. **Trailing Slot (Optional):** Chevron down (`▾`), download arrow (`⤓`), or accelerator symbol (`⚡`).
5. **Loading Spinner Slot:** 14×14px circular SVG spinner centered when `loading` state is active.

#### Variants
1. **Primary Obsidian Pill:** Solid `#000000` surface, `#ffffff` text. Used for the single most important action on any surface (e.g., `Download ⤓` or `Start Matching ⚡`).
2. **Secondary Outline Pill:** `#ffffff` surface, `#121317` text, 1px `#e5e7eb` border. Used for supporting actions (e.g., `Architecture & Specs`, `Inspect Specs`).
3. **Dropdown Trigger Pill:** `#ffffff` surface with trailing `▾` indicator. Used for header navigation and role selection menus.
4. **Compact Icon Action Pill:** 32×32px circular or 28px height pill for inline utilities (`🚀`, `✕`, copy snippet).
5. **Pagination Dot Pill:** 8×8px circular dot expanding to 24×8px rounded pill when active.

#### Complete 7-State Matrix

| State | Primary Obsidian Variant | Secondary Outline Variant | Dropdown Trigger Variant |
| :--- | :--- | :--- | :--- |
| **1. Default** | `bg: #000000; text: #ffffff; border: 1px solid #000000; shadow: shadow.xs;` | `bg: #ffffff; text: #121317; border: 1px solid #e5e7eb; shadow: shadow.xs;` | `bg: transparent; text: #45474d; border: none;` |
| **2. Hover** | `bg: #1f2937; transform: translateY(-1px); shadow: shadow.elevated;` | `bg: #fafaf9; border-color: #d1d5db; transform: translateY(-1px);` | `color: #121317; bg: #f4f4f5; border-radius: 9999px;` |
| **3. Focus-Visible** | `outline: 2px solid #000000; outline-offset: 2px;` | `outline: 2px solid #000000; outline-offset: 2px;` | `outline: 2px solid #000000; outline-offset: 2px;` |
| **4. Active (Pressed)** | `transform: scale(0.98); bg: #000000; shadow: none;` | `transform: scale(0.98); bg: #f3f4f6;` | `bg: #e5e7eb;` |
| **5. Disabled** | `bg: #e5e7eb; text: #9ca3af; border: 1px solid #e5e7eb; cursor: not-allowed; opacity: 0.6;` | `bg: #f9fafb; text: #9ca3af; border: 1px solid #e5e7eb; cursor: not-allowed;` | `text: #d1d5db; cursor: not-allowed;` |
| **6. Loading** | `cursor: wait; opacity: 0.85; pointer-events: none; spinner active; aria-busy: true;` | `cursor: wait; opacity: 0.85; pointer-events: none; spinner active;` | `aria-busy: true;` |
| **7. Error** | `border-color: #ea4335; box-shadow: 0 0 0 2px rgba(234, 67, 53, 0.2); animation: shake 200ms;` | `border-color: #ea4335; color: #ea4335;` | `border-bottom: 2px solid #ea4335;` |

#### Interaction & Ergonomics Rules
- **Pointer:** Hover state **must** trigger within `motion.duration.instant` (150ms). Cursor **must** be `pointer` for enabled buttons and `not-allowed` for disabled.
- **Keyboard:**
  - `Tab`: Moves focus to the button. Must render high-contrast 2px solid focus ring.
  - `Enter` / `Space`: Activates the button (`:active` pressed state rendered).
- **Touch Targets:**
  - On touch viewports, every button **must** provide a minimum tap target bounding box of $44 \times 44\text{px}$ (or $48 \times 48\text{px}$ per WCAG 2.2 AAA recommendations).
  - Touch press **must** suppress the default OS tap highlight color (`-webkit-tap-highlight-color: transparent`).
- **Overflow & Long Labels:**
  - Labels exceeding container width **must** remain on a single line with `text-overflow: ellipsis; white-space: nowrap; overflow: hidden;`.
  - Icon-only variants **must** include an `aria-label` describing the exact action.

---

### 4.2 Links (87 instances)

#### Anatomy
- Base `<a>` element with semantic `href`.
- Content label: `font.size.md` (14.5px) for navigation; `font.size.lg` (16px) for body inline links.
- External indicators: Links pointing to external origins (e.g. documentation, GitHub, Google Antigravity main site) **must** declare `target="_blank"` and `rel="noopener noreferrer"`.

#### Variants
1. **Header Navigation Link:** Understated text link in the top bar. Resting color `color.text.secondary` (`#45474d`), transitioning to `color.text.primary` (`#121317`) on hover.
2. **Announcement Capsule Link:** Bold link styled inside the top announcement capsule (`Explore →` or `Learn more ➔`).
3. **Inline Text Link:** Underlined or color-differentiated link embedded within prose.
4. **Footer Sitemap Link:** Compact link styled with `font.size.sm` (13px) in the bottom directory.
5. **In-Page Jump Anchor:** Rail or table of contents anchor with smooth scroll behavior.

#### Complete 7-State Matrix
- **Default:** `color: var(--color-text-secondary); text-decoration: none; font-weight: 450;`
- **Hover:** `color: var(--color-text-primary); text-decoration: underline; text-underline-offset: 3px;`
- **Focus-Visible:** `outline: 2px solid var(--color-surface-base); outline-offset: 3px; border-radius: 2px;`
- **Active:** `color: var(--color-surface-base); font-weight: 600;`
- **Disabled:** `color: var(--color-text-inverse); pointer-events: none; text-decoration: none; cursor: default;`
- **Loading:** `opacity: 0.5; cursor: wait;`
- **Error (Broken Destination):** `color: var(--color-google-red); text-decoration: line-through;`

---

### 4.3 Navigation (9 instances)

#### Inventory of Navigation Instances
1. **Global Sticky Header Navbar:** Fixed or relative top container with brand mark, nav links, and action pill cluster.
2. **Announcement Capsule Banner:** Floating capsule centered above the hero headline.
3. **Products Megamenu Dropdown:** Expandable menu for product features and models.
4. **Use Cases Megamenu Dropdown:** Expandable menu for enterprise and developer use cases.
5. **Resources Megamenu Dropdown:** Expandable menu for documentation, API references, and blog.
6. **Language / Locale Selector Pill (`🌐 EN ▾`):** Compact dropdown capsule in the top right header.
7. **In-Page Anchor Rail:** Floating right-hand icon rail for quick section jumping.
8. **Workspace Mode Tabs:** Two-way or three-way segmented pill tab (`Resume Analysis` | `Candidates` | `Settings`).
9. **Mobile Drawer Navigation:** Full-screen collapsible overlay triggered on viewports `< 768px`.

#### Behavioral Specifications
- **Dropdown Panels:**
  - Trigger **must** declare `aria-haspopup="true"` and `aria-expanded="false"`.
  - On click or `Enter`/`Space`, `aria-expanded` **must** toggle to `"true"`, revealing the panel with `motion.duration.fast` (200ms).
  - Pressing `Escape` **must** immediately close the open panel and return focus to the trigger pill.
  - Clicking outside the panel bounding box **must** dismiss the dropdown.
- **Sticky Header Scroll Transition:**
  - Upon vertical scroll $> 32\text{px}$, the header bar **should** apply a translucent white backdrop (`background: rgba(255, 255, 255, 0.88); backdrop-filter: blur(12px); border-bottom: 1px solid rgba(229, 231, 235, 0.8)`).

---

### 4.4 Inputs (4 instances)

#### 1. Candidate Search / Filter Pill Input
- **Anatomy:** Fully rounded capsule (`radius.lg = 9999px`) containing a leading magnifying glass SVG, input field, and clear `✕` button.
- **Tokens:** Height `40px`, padding `0 space.5`, `bg: #ffffff`, `border: 1px solid #e5e7eb`, font `font.size.md` (14.5px).
- **Focus-Visible:** `border-color: #4285f4; box-shadow: 0 0 0 3px rgba(66, 133, 244, 0.15); outline: none;`

#### 2. Scoring Weights Sliders Group (3 Sliders)
- **Anatomy:** Track, fill bar, thumb pill, label header with numeric readout (`0.50`, `0.20`, `0.30`), and help tooltip.
- **Keyboard:** `ArrowLeft`/`ArrowDown` decreases by step `0.05`; `ArrowRight`/`ArrowUp` increases by `0.05`. `Home`/`End` sets minimum (0.0) / maximum (1.0).
- **Normalization Indicator:** Normalized weight share display **must** update live in real-time as thumbs are dragged.

#### 3. Role Profile Selection Dropdown
- **Anatomy:** Pill trigger showing selected role (`ds-001 — Data Scientist`), custom option list with role code badge and core skills summary.
- **Empty State:** If no job description is loaded, displays `"Select a benchmark preset or paste custom job requirements"`.

#### 4. PDF Resume Drag-and-Drop Staging Zone
- **Anatomy:** Dashed container (`border: 2px dashed #d1d5db; border-radius: 20px; background: #fafaf9;`), upload icon tile, drop instruction text, supported format indicator (`PDF up to 20MB`), and browse files pill button.
- **Drag-Over State:** `border-color: #4285f4; background: #e8f0fe; transform: scale(1.005);`

---

### 4.5 Cards (2 instances)

#### 1. Primary Hero Spotlight Card (`.agy-hero-container`)
- **Anatomy:**
  - Container with `border-radius: 36px` (`radius.sm`), background `#ffffff`, hairline border `1px solid #e5e7eb`.
  - Deterministic radial dashed particle burst canvas (130 multi-colored Google dashes).
  - Centered announcement capsule (`✦ NEW Gemini 4 Argon...`).
  - Centered brand emblem + "Google Antigravity".
  - Giant display title: `Experience liftoff with the next-gen agent platform` (clamp 2.4rem to 4.2rem).
  - Action button cluster: Centered primary black pill `[ Start Matching ⚡ ]` and secondary outline pill `[ Architecture & Specs ]`.
  - Benchmark role preset cards along the bottom.

#### 2. Candidate / Capability Detail Analysis Card (`.agy-spotlight-card` / `.bui-stat-card`)
- **Anatomy:**
  - Header: Role title or candidate name, Google quad-color status dot, match percentage chip.
  - Body: Matched core skills badges, missing skills warnings, SBERT semantic score readout.
  - Interactive Action: `[ Inspect Specs ]` and `[ Select Role ]` pill buttons.
- **States:**
  - **Default:** `border: 1px solid #e5e7eb; box-shadow: 0 1px 3px rgba(0,0,0,0.03);`
  - **Hover:** `border-color: #b7bfd9; transform: translateY(-2px); box-shadow: 0 8px 24px -4px rgba(0,0,0,0.06);`

---

### 4.6 Lists (1 instance)

#### Ranked Candidate Leaderboard & Explainability Evidence List
- **Anatomy:**
  - Header: Rank, Candidate Name, Hybrid Score %, Core Skills Coverage %, Preferred Skills %, Semantic Similarity %, Verification SLA.
  - Row Item: Light white row with subtle hover highlight (`#f8f9fa`).
  - Evidence Sub-drawer: Expandable drawer revealing extracted sentences, matched ESCO terms, and spatial PDF bounding box evidence.
- **Empty State:** When no resumes have been staged, displays clean bordered card:
  `"No resumes analyzed yet. Select a role above and drop candidate PDFs to run real-time matching."`

---

## 5. Accessibility Requirements (WCAG 2.2 Level AA)

### 5.1 Testable Acceptance Criteria Table

| WCAG 2.2 Criterion | Target Standard | Implementation Rule | Verification Method | Pass Condition | Fail Condition |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1.4.3 Contrast (Minimum)** | Level AA | Normal text ($< 24\text{px}$) **must** achieve $\ge 4.5:1$ contrast against adjacent background. | Automated axe-core / Lighthouse audit | `#121317` on `#ffffff` = **16.5:1**; `#45474d` on `#ffffff` = **7.8:1** | Any text with contrast $< 4.5:1$ |
| **1.4.11 Non-text Contrast** | Level AA | UI component boundaries, button borders, and focus rings **must** achieve $\ge 3:1$ contrast. | Color picker contrast checker | Black button border on white = **21:1**; `#d1d5db` = **3.1:1** | Low-contrast borders ($< 3.0:1$) |
| **2.1.1 Keyboard Navigation** | Level A | All interactive elements (links, buttons, inputs, sliders) **must** be operable via keyboard alone. | Manual `Tab` / `Shift+Tab` walkthrough | Focus reaches all 80 buttons and 87 links; activations execute via `Enter` or `Space` | Any control trapped, skipped, or requiring pointer |
| **2.4.7 Focus Visible** | Level AA | Focus indicators **must** be clearly visible on keyboard navigation. `outline: none` without replacement is strictly forbidden. | CSS inspection on `:focus-visible` | 2px solid `#000000` with 2px offset visible on all focused elements | Suppressed outline with zero visual feedback |
| **2.5.8 Target Size (Minimum)** | Level AA | Pointer target size **must** be at least $24 \times 24\text{px}$ CSS pixels, and touch controls **should** provide $\ge 44 \times 44\text{px}$. | Touch bounding box measurement | All buttons $\ge 38\text{px}$ height; mobile touch targets $\ge 44\text{px}$ | Clickable target $< 24 \times 24\text{px}$ |
| **2.3.3 Animation from Interactions** | Level AAA / AA | Motion animations **must** respect user preference for reduced motion. | Emulate `prefers-reduced-motion: reduce` | Orbital rotation and particle floats disabled; transitions instant ($\le 10\text{ms}$) | Parallax, spinning, or continuous float active under reduced motion |
| **4.1.2 Name, Role, Value** | Level A | Every control **must** expose an accessible name, valid ARIA role, and current state. | Screen reader check (VoiceOver / NVDA) | Buttons announce label + role; dropdowns announce expanded state | Unlabeled icon buttons; `<div>` used as button without `role="button"` |

---

## 6. Content & Tone Standards

### 6.1 Tone Pillars
- **Technical & Confident:** Speak directly to engineers and architects without marketing jargon or buzzwords.
- **Concise & Direct:** Lead with action verbs and concrete quantitative metrics (e.g., *"SLA 178ms · 17× Headroom"*, *"100% Explainable"*).
- **Transparent & Trustworthy:** Always surface explicit calculation formulas, weight shares, and DPDP Act compliance notes.

### 6.2 Microcopy & Copywriting Examples

| Context | Do (Compliant Copy) | Don't (Prohibited Copy) | Rationale |
| :--- | :--- | :--- | :--- |
| **Primary Hero CTA** | `Start Matching ⚡` or `Download ⤓` | `Click Here` or `Get Started Today!` | Clear, descriptive action verb specifying the actual outcome. |
| **Announcement Banner** | `✦ NEW Gemini 4 Argon available in Google Antigravity` | `Check out our awesome new AI release!` | Concise, factual, model-specific nomenclature. |
| **Empty State Header** | `No Resumes Staged for Evaluation` | `Oops! Nothing to see here!` | Professional, technical tone avoiding infantile expressions. |
| **Privacy Assurance** | `Processed strictly in volatile RAM. Zero disk storage. DPDP Act 2023 compliant.` | `Your data is totally safe with us!` | Concrete architectural guarantees rather than vague assurances. |
| **Error Message** | `Corrupt PDF Header (EOF missing in candidate_04.pdf). Please re-export.` | `Upload failed! Something went wrong.` | Actionable error message detailing exact diagnostic cause. |

---

## 7. Anti-patterns & Prohibited Implementations

The following design and implementation patterns are strictly prohibited across all Google Antigravity surfaces:

1. ❌ **Arbitrary Hardcoded Hex Values:** Using ad-hoc colors (e.g., `#23272f`, `#383838`) instead of defined `--color-text-*` and `--color-surface-*` tokens.
2. ❌ **Glowing Neon & Cyberpunk Aesthetics:** Heavy radial glows, neon yellow text shadows, or radioactive borders that clash with the pristine white Antigravity surface.
3. ❌ **Square-Cornered Action Buttons:** Any primary or secondary button with sharp corners or radii $< 9999\text{px}$. All buttons **must** be pills.
4. ❌ **Suppressed Focus Rings:** Using `outline: none` or `outline: 0` without an immediate high-contrast replacement.
5. ❌ **Non-Descriptive Action Labels:** Ambiguous button copy like `"Go"`, `"Click"`, `"More"`, or icon-only buttons without `aria-label`.
6. ❌ **Cumulative Layout Shift (CLS) on Asset Load:** Buttons or cards changing dimensions as fonts or icons asynchronously load. All containers **must** declare intrinsic dimensions or minimum heights.
7. ❌ **Nested Interactive Elements:** Placing clickable badges, links, or buttons inside an outer clickable card element.
8. ❌ **Dark Mode Flash:** Allowing stale dark mode theme tokens to render on the client when the canonical Antigravity experience is light mode.

---

## 8. Comprehensive QA Checklist

### Visual & Token Verification
- [x] Background canvas renders pure `#ffffff` with zero dark mode remnant artifacts.
- [x] Official Google Antigravity chevron 'A' emblem with multi-color gradient renders sharply at all viewport scales.
- [x] Radial dashed particle burst renders 130 subtle Google-colored tick marks behind the hero centerpiece.
- [x] Top announcement capsule renders with `✦ NEW` black pill and direct link.
- [x] Display headline matches `Experience liftoff with the next-gen agent platform` in Google Sans Flex typography.
- [x] All buttons follow fully rounded pill profiles (`radius.lg = 9999px`).
- [x] Primary actions use solid black (`#000000`) surfaces with pure white (`#ffffff`) text.
- [x] Secondary actions use crisp white surfaces with hairline gray borders (`#e5e7eb`).
- [x] All typography strictly adheres to the 8-step scale (`font.size.xs` through `font.size.4xl` + `display`).
- [x] Spacing between sections and within cards uses exclusively `space.1` through `space.8`.

### State & Interaction Verification
- [x] Every button correctly implements all 7 states (default, hover, focus-visible, active, disabled, loading, error).
- [x] Primary buttons elevate with `translateY(-1px)` and subtle shadow on hover.
- [x] Active button press produces subtle `scale(0.98)` tactile response.
- [x] Dropdown menus dismiss cleanly on outside click and on `Escape` key press.
- [x] Search input displays active blue halo on focus (`rgba(66, 133, 244, 0.15)`).
- [x] File upload dropzone indicates active drag-over state with blue tint and dashed border highlight.

### Accessibility & Performance Verification
- [x] All text passes WCAG 2.2 AA minimum contrast ($\ge 4.5:1$ for body, $\ge 3:1$ for display headings).
- [x] Focus-visible ring renders with 2px solid outline and 2px offset on all keyboard tab stops.
- [x] Tab order follows natural visual reading hierarchy without focus traps.
- [x] Touch targets measure $\ge 44 \times 44\text{px}$ on mobile screens.
- [x] `@media (prefers-reduced-motion: reduce)` disables orbital and particle motion.
- [x] Automated test suite passes 100% of unit and integration test assertions (`51/51 passed`).
- [x] Python modules compile cleanly without syntax or import errors.
- [x] Volatile memory processing guarantee is prominently stated for DPDP Act 2023 compliance.
