# Design — Malayalam Tourist Translation & Transliteration System

| | |
|---|---|
| **Status** | Design specification — UI is **planned** (built in Phase 14) |
| **Created** | 2026-09-30 |
| **Principle** | Simple, academic, tourism-focused. **Do not overdesign** — this is an NLP mini-project, not a product launch. |

---

## 1. Visual concept

- A **single-screen translation workspace**: choose direction → type → translate → read result with category and entities beside it.
- Tourism flavor through a Kerala-inspired palette (backwater greens, warm accent) — used as accents only; content stays high-contrast and legible.
- Everything on one page; no navigation, no login, no tabs beyond the essentials.
- Built with **Streamlit** per `Architecture.md` §12 — the design maps directly to Streamlit widgets (no custom frontend framework).

## 2. Color palette

| Role | Color | Hex (planned) | Usage |
|---|---|---|---|
| Primary | Deep teal | `#00695C` | Header, Translate button |
| Secondary | Backwater green | `#2E7D32` | Active direction, success states |
| Accent | Warm saffron | `#F9A825` | Category chip, highlights (used sparingly) |
| Background | Off-white | `#FAFAF7` | Page background |
| Surface | White | `#FFFFFF` | Cards/panels (input, output) |
| Text | Near-black | `#212121` | Body text |
| Muted text | Gray | `#757575` | Labels, hints |
| Error | Red | `#C62828` | Error states only |

Rules: text/background pairs must meet readable contrast (target WCAG AA — **verify during Phase 14**, don't assume); color is never the *only* signal (errors also carry text; the category chip also shows its label).

## 3. Typography

| Context | Font (planned) | Notes |
|---|---|---|
| Malayalam text (input & output) | **Noto Sans Malayalam** (+ system fallback) | Must render all Malayalam glyphs — no tofu boxes |
| Latin text (English/Manglish) | Inter / system sans-serif | Plain, readable at small sizes |
| Numbers/metrics | Same as Latin | Tabular figures where available |

- Malayalam line-height ≥ 1.6 (Malayalam glyphs stack above/below the baseline); no negative letter-spacing on Malayalam.
- Font strategy carries over to matplotlib EDA figures (`Architecture.md` §10) — a Malayalam-capable font must be registered there too (Phase 6 validation checks this).

## 4. Layout

```
┌──────────────────────────────────────────────────────────┐
│  Malayalam Tourist Translator            [theme accent]  │
├──────────────────────────────────────────────────────────┤
│  Translation Direction: [ English → Malayalam ▼ ]        │
│  Tourism Category (auto): [ 🚕 Transportation ] (or ▼)   │
├───────────────────────────────┬──────────────────────────┤
│  INPUT                        │  OUTPUT                  │
│  ┌─────────────────────────┐  │  ┌────────────────────┐  │
│  │ Enter your sentence     │  │  │ മലയാള വാക്യം / EN  │  │
│  │ (multi-line, grows)     │  │  │ translation here   │  │
│  └─────────────────────────┘  │  └────────────────────┘  │
│  [ ⏻ Translate ]  [ ✕ Clear ]│                          │
│                               │  Detected Category:      │
│                               │   Transportation         │
│                               │  Detected Entities:      │
│                               │   Location: Railway      │
│                               │            Station       │
│                               │   Money: ₹ 500           │
└───────────────────────────────┴──────────────────────────┘
        Status / error messages (inline, below button)
```

- Two-column desktop layout (input | output+entities); single column on narrow screens (§12).
- Order on the page: direction → input → button → output → category → entities → status.
- Header is one line; no sidebar, no menu.

## 5. Input area

- Multi-line text area, placeholder: `Enter your sentence`.
- Gentle live checks (client-side only, no NLP): empty/whitespace-only input disables the Translate button; character counter appears only beyond a soft limit (limit **DECISION REQUIRED** at Phase 14, tied to model constraints — do not guess a model max length).
- Accepts English, Malayalam, or Manglish text depending on the selected direction; mismatch detection is advisory (§10).
- No input persistence (NFR-8): nothing saved between sessions or sent anywhere.

## 6. Translation direction selector

A single selectbox, default first option, four options only:

```
[ English → Malayalam   ▼ ]
  Malayalam → English
  Manglish → English
  English → Manglish
```

- Switching direction clears or keeps the input? → **Keep input** (faster back-and-forth) but re-run the script-mismatch advisory on next Translate. (**ASSUMPTION**, revisited in Phase 14.)
- The selector is the only place direction is chosen; the pipeline receives exactly this enum (D1–D4 per `PRD.md` §6).

## 7. Tourism category

- **Auto-detected** category displayed as a chip (accent color) with its label — e.g. `Transportation`, per the eight categories in `PRD.md` §7.
- Optional **manual override** dropdown (the eight categories + `Auto`) for when detection is wrong — overrides only affect the displayed category, not the translation itself (translation is category-agnostic; **ASSUMPTION**, revisit if category-conditioned behavior is ever added).
- Empty input → show `Category: —`.
- Category detection is rule/keyword-based first (Phase 8); accuracy is measured, not assumed.

## 8. Translation result

- Output panel mirrors the input script:
  - D1/D4 target Malayalam/Manglish renders with the Malayalam font stack / Latin font respectively (§3, §14).
- Panel header shows the target language name (`Output (Malayalam)`).
- Copy-friendly plain text (Streamlit default selection works); no formatting injected into the translation string.
- While translating, the output panel shows a loading state (§11) — it is **never** pre-filled with placeholder or guessed text (Rules §4).

## 9. Entity display

Below the output, a simple labeled list (no maps, no cards):

```
Detected Entities
  Location : Railway Station
  Money    : ₹ 500
  Phone    : +91 98470 12345
  Date     : 12 December
```

- One row per entity; type label in muted text, value in body text.
- Entity types limited to PRD FR-6 (locations, hotels, restaurants, people, organizations, dates, money, phone numbers, prices, URLs).
- No entities → show `None detected` (not a blank void).
- Values come straight from `src/ner/extractor.py` — the UI does no entity logic.

## 10. Error states

| Condition | Behavior |
|---|---|
| Empty input | Button disabled + hint `Please enter a sentence.` (no API call made) |
| Script/direction mismatch (e.g., Malayalam text while D1 English→Malayalam selected) | Advisory warning `This looks like Malayalam text; English is expected for this direction. Translate anyway?` — Translate still allowed (tourists mix scripts) |
| Model not loaded/downloaded | Error card: `Translation model is not available. Run the setup command (see README).` — **no fabricated output** (Rules §4) |
| Translation runtime error | Error card with the actual short reason + `Try again`; full detail to console log |
| Internal/unexpected error | Generic error card; never a partial fake result |

- Errors render **inline** under the button/status line in the error color (§2) with an icon *and* text (never color-only, §2).
- Every error path is exercised by the Phase 14 manual test script.

## 11. Loading states

- On Translate: button shows `Translating…` and is disabled (no double-submit); output panel shows a spinner + `Translating…` caption.
- Page-load model note: if model loading is lazy, show a one-time `Loading model…` info line — first translation may take longer; subsequent ones should be faster (actual timings recorded in Phase 13, not promised here).
- Loading UI is Streamlit's built-in spinner/`st.status` — no custom animation work.

## 12. Mobile responsiveness

- Single-column stack on narrow screens: direction → input → button → output → category → entities (DOM order already matches §4's reading order, so no reordering needed).
- Tap targets ≥ ~44 px (Streamlit defaults acceptable — verify in Phase 14).
- No hover-only information; nothing requires a wide screen.
- Verification: browser dev-tools at ~375 px width; checklist item in Phase 14.

## 13. Malayalam Unicode support

- UTF-8 end-to-end; input value passed through unchanged into preprocessing (NFC normalization happens in `src/preprocessing/`, not in the UI).
- Malayalam font stack (§3) applied to both input widget and output panel so the user's Malayalam never renders as boxes.
- No JS string slicing/length hacks on Malayalam in the UI layer (grapheme clusters) — only safe whole-string operations.
- Visual acceptance test: the spec reference sentence `എനിക്ക് ഒരു ടാക്സി വേണം.` renders identically in input and output panels (Phase 14).

## 14. Manglish display

- Manglish is **Romanized Malayalam** → rendered as ordinary Latin text (same font as English), never given a "language badge" implying it is a separate language.
- Direction labels spell it out honestly: `English → Manglish (romanized Malayalam)` in a tooltip/help caption.
- Input in D3 accepts informal romanization variants (normalization happens in `src/transliteration/mg_to_ml.py`, Phase 11 — UI shows the *normalized* Malayalam in an optional expander `Show normalized Malayalam` so users see the intermediate step. **Planned**, nice-to-have: cut first if time-constrained — do not overdesign).

## 15. Accessibility

- **Labels:** every widget has a visible label or `aria-label` (`Translation Direction`, `Input sentence`, `Translate`).
- **Keyboard:** full flow operable by Tab/Enter (Streamlit default — verify); Translate button reachable without mouse.
- **Screen readers:** status/error messages rendered as text (not canvas/images); output panel updates announced via Streamlit's native message region (verify in Phase 14; limitations documented honestly if the framework constrains this).
- **Contrast:** text/background pairs target WCAG AA (§2) — measured with a contrast checker in Phase 14, not assumed.
- **Motion:** no flashing/animated elements; loading uses a standard spinner.
- **Language:** direction change updates the visible labels (`Output (Malayalam)` etc.) so the user always knows which language they are reading.

---

*Scope guardrail: any UI feature not specified here (chat history, auth, maps, image input, dark mode, themes beyond the palette above) is out of scope for this mini-project. Implementation follows `Phases.md` Phase 14.*
