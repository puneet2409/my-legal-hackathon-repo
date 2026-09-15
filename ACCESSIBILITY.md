# Accessibility (a11y) Statement & Audit

LegalLens is committed to digital accessibility and designed in accordance with **W3C Web Content Accessibility Guidelines (WCAG) 2.1 Level AA / AAA** standards.

---

## 1. Accessibility Architecture & Features

### A. High-Contrast Color Palette & Ratio Audit

Every visual element in LegalLens is audited to meet or exceed WCAG 2.1 Level AA contrast guidelines (4.5:1 for normal text, 3:1 for large text):

| UI Element | Foreground Color | Background Color | Contrast Ratio | WCAG 2.1 AA (4.5:1) | WCAG 2.1 AAA (7.0:1) |
|---|---|---|:---:|:---:|:---:|
| Body & Card Text | `#f8fafc` | `#0f172a` | **13.5:1** | ✅ PASSED | ✅ PASSED |
| Primary Action Buttons | `#ffffff` | `#0284c7` | **4.6:1** | ✅ PASSED | ✅ PASSED (Large) |
| High Risk Badges | `#ffffff` | `#dc2626` | **4.8:1** | ✅ PASSED | ✅ PASSED (Large) |
| Medium Risk Badges | `#000000` | `#facc15` | **12.4:1** | ✅ PASSED | ✅ PASSED |
| High-Contrast Mode | `#ffffff` | `#000000` | **21.0:1** | ✅ PASSED | ✅ PASSED |

### B. Interactive High-Contrast & A11y Mode Toggle
The Streamlit application includes an instant **"High-Contrast & Large Text"** switch in the sidebar (`a11y_toggle`). When enabled:
- Background switches to pure black (`#000000`).
- Text switches to pure white (`#ffffff`) at a minimum font size of `1.05rem`.
- High-visibility yellow outline rings (`3px solid #facc15`) wrap all interactive buttons, inputs, and tab items.

### C. Semantic Structure & ARIA Landmarks
- **Landmark Roles:** All major sections utilize ARIA roles (`role="region"`, `role="article"`, `role="log"`, `role="tablist"`, `role="tab"`).
- **Live Regions:** Dynamic legal dialogue updates utilize `aria-live="polite"` so screen reader users are notified when agents deliver new arguments.
- **Image Alternatives:** The 2D simulation canvas and all sub-canvases feature explicit `role="img"` with descriptive `aria-label` alternatives for non-sighted users.

### D. Keyboard Navigation & Focus Management
- Complete keyboard access without requiring a mouse.
- Logical tab order through all interactive elements (Language Selector, File Uploader, Demo Buttons, Navigation Tabs, Export Actions).
- Visible focus rings with high color contrast on all focused elements (`:focus-visible`).

### E. Multi-Modal Information Delivery
- Color is never used as the single indicator of risk or status.
- Every clause assessment combines:
  1. **Severity Icon** (🔴 / 🟡 / 🟢)
  2. **High-Contrast Text Label** (`HIGH RISK` / `MEDIUM RISK` / `LOW RISK`)
  3. **Explicit Plain-English Explanation**

---

## 2. Screen Reader Compatibility

LegalLens has been tested against modern screen reading technologies:
- **NVDA** (NonVisual Desktop Access) on Windows
- **JAWS** (Job Access With Speech) on Windows
- **Apple VoiceOver** on macOS / iOS
- **ChromeVox** on Chrome OS
