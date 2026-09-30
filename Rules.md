# Rules — Malayalam Tourist Translation & Transliteration System

| | |
|---|---|
| **Scope** | Binding development rules for all team members and AI coding assistants working on this repository |
| **Status** | Active from 2026-09-30 (documentation phase) |
| **Precedence** | Explicit task instructions → this file → `PRD.md` → `Architecture.md` → `Phases.md` → `Design.md` |

Marker conventions (used in code, docs and `Memory.md`):

- **NOT YET CALCULATED** — the value exists but has not been computed yet
- **DECISION REQUIRED** — an unresolved choice that blocks related work
- **ASSUMPTION** — an unverified guess, must be labeled as such
- **planned** — specified in documentation, not yet implemented

---

## 1. Academic integrity

1. This is coursework. All reports, slides and documentation must reflect work actually done by the team.
2. Cite every external resource: datasets (source + license), pretrained models (name + source + license), papers
   (IndicTrans2, Lesk, BLEU, etc.), and any borrowed code snippets or algorithms (with references).
3. Never present AI-generated or borrowed code as your own understanding — you must be able to explain every module
   in the repository (be ready for viva/demo questions).
4. Do not copy another team's report, code, or evaluation numbers.
5. Contributions of each team member are recorded honestly in the final report (team roster: Ronald Aaron Tamil
   Arasan, Sharon Sam, Sam Manoj — see `Memory.md`).
6. The documentation must accurately connect the project to course Experiments 1–8 without over-claiming: an
   experiment that ends up unused is reported as *evaluated but not adopted*, with the reason.

## 2. Dataset licensing

1. Only datasets whose license permits the intended academic use are collected. FOSS/preferably permissive
   licenses (e.g., CC-BY, MIT) — **no pirated, scraped-without-permission, or license-ambiguous data**.
2. For **every** dataset, record in `Memory.md` § Dataset before any code uses it:
   name · source URL · license · number of sentence pairs (counted, not estimated) · preprocessing performed ·
   train/validation/test split sizes.
3. **No fabricated dataset sizes** anywhere — if not downloaded and counted, the entry does not exist.
4. `data/raw/` is immutable. Cleaning always writes to `data/processed/`; raw files are never edited or deleted.
5. The frozen test sets (`data/test/`) are created once; after the first evaluation run they are never modified.
   Changing a test set invalidates all previously recorded scores (which must then be marked superseded).
6. If a candidate source (e.g., Samanantar, BPCC, tourism-domain parallel data) turns out to be unusable, record
   that fact and the reason — absence is data, fabrication is not.

## 3. No fabricated results

1. Any metric, count, accuracy, score or timing that has not been produced by an actual run is written as
   **NOT YET CALCULATED**.
2. All reported numbers in `Memory.md`, the final report and slides must be reproducible from documented commands
   (§15) and must come with their configuration (metric setup, test set version, hardware for timings).
3. Never copy example numbers from papers, tutorials or AI suggestions into results sections.
4. Optimistic rounding, cherry-picking best runs, or evaluating on data used for tuning is forbidden: report the
   agreed metric configuration over the frozen test set, first run included.
5. When an experiment fails or is abandoned, the failure is documented (§16), not hidden.

## 4. No fabricated translations

1. Output text shown as "the translation" must come from the actual pipeline. The UI must never display a
   hand-written, cached-from-elsewhere, or guessed translation as model output.
2. If the model is unavailable or errors, the UI shows an **error state** — it must not fall back to some
   hardcoded phrase table while pretending to be the model (Rules §13).
3. Reference examples in the documentation (e.g., "I need a taxi." → "എനിക്ക് ഒരു ടാക്സി വേണം.") are spec-provided
   *expected* pairs used for tests and curation — they are labeled as reference expectations, never as measured
   output.
4. Any human-corrected translation used as data must be marked as human-authored (curated test/phrase lists), with
   the authoring process described.

## 5. Malayalam Unicode handling

1. **UTF-8 everywhere**: source files, data files (explicit encoding on every `open()` — never rely on platform
   default), CSV/JSON, logs, database-free storage.
2. Normalize with Unicode **NFC** at system boundaries (ingest, storage); use one convention and record it in
   `Memory.md` once chosen (Phase 1/4 decision).
3. Malayalam text must survive round-trips: `normalize(save(load(text))) == normalize(text)` — guarded by unit
   tests (§15).
4. Never manipulate Malayalam with naive byte/char assumptions: no truncating mid-cluster, no per-codepoint case
   tricks (Malayalam has no case), no stripping combining marks.
5. Word/character counting must be defined precisely (code points vs grapheme clusters vs words) and documented;
   counts in EDA/word clouds state which definition was used.
6. Display and rendering (UI, matplotlib figures) must be checked for missing-glyph boxes; a figure showing tofu
   boxes is a failed artifact, not a deliverable (Phases §6 validation).

## 6. Manglish normalization

1. Manglish = **Romanized Malayalam**. It is never treated, documented, or implemented as an independent natural
   language.
2. Choose **one standard Manglish romanization scheme** for normalization (candidates: ITRANS-like, ISO-15919-like,
   or the scheme dominant in the collected data). The choice is **DECISION REQUIRED** at Phase 11; the decision and
   rationale go to `Memory.md` § Decisions. All Mg work uses this scheme.
3. Normalization steps (planned): lowercase for matching (English/Latin case rules apply to Manglish), whitespace
   collapse, punctuation policy, optional diacritic-fold variants — each step recorded.
4. Manglish → Malayalam conversion happens **before** any English translation (route D3); Malayalam → Manglish
   happens **after** English→Malayalam (route D4). No direct Manglish↔English model.
5. Round-trip behavior is tested: for curated pairs, `Mg → Ml → Mg` stability is measured and reported honestly
   (expected imperfect; record what actually happens).

## 7. Translation model usage

1. The project uses a **pretrained** multilingual translation model; **training from scratch is forbidden** by
   scope (PRD Non-goals).
2. The candidate model family is **IndicTrans2** (supports English ↔ Malayalam). When downloaded, record in
   `Memory.md` § Model: exact checkpoint name, version/revision, source URL, language codes/tags used by that
   model, license, parameter count if published, and download date.
3. Never claim the team trained or owns the model. Report language: "we *use* pretrained model X (citation)".
4. If fine-tuning is ever performed: document it as a **separate** experiment (data, epochs, hardware, before/after
   metrics); never mix fine-tuned and pretrained results under one label.
5. Model files live in `models/` (gitignored). The project must run without re-downloading once the model exists
   locally; document the exact download command in `Memory.md` § Commands when established.
6. Metric results are always tied to the model identity (a different checkpoint = different results, not
   comparable without saying so).

## 8. Preprocessing rules

1. One preprocessing implementation (`src/preprocessing/`) shared by translation input, corpus building, NER,
   n-gram counts and evaluation — no divergent copies in other modules.
2. The cleaner supports modes (e.g., `mode="translation"` lighter vs `mode="corpus"` heavier); the mode used for
   each task is recorded.
3. Preprocessing must be Malayalam-aware (script-preserving tokenization, no ASCII-only assumptions, no lossy
   transliteration hidden inside "cleaning").
4. Train/test leakage is forbidden: test sets are pre-split and frozen; no test text may enter corpus statistics,
   n-gram counts, keyword lists, or classifier features.
5. Keyword lists and pattern inventories used for category/entity detection must come from training data or
   documented domain knowledge — not from reading the test set.
6. Preprocessing changes after evaluation started invalidate comparability: re-run affected evaluations and mark
   old results superseded.

## 9. NER rules

1. Entity types are fixed by PRD FR-6; extending the list is allowed only with documentation + evaluation updates.
2. NER quality is **measured** (precision/recall/F1) against a hand-labeled sample; the labeling process
   (who labeled, how many sentences, agreement checks if any) is documented in `Memory.md`.
3. Never state NER is "accurate" without numbers; unmeasured = **NOT YET CALCULATED**.
4. The merge policy between the regex layer (E3) and chunking layer (E5) is documented before evaluation (Phase 8,
   **DECISION REQUIRED**), then kept stable.
5. Hand-labeled data used for evaluation stays out of pattern-development loops (develop on train/dev, evaluate on
   held-out labels).

## 10. WSD rules

1. Implement Lesk-style disambiguation (E7) with an explicitly documented sense-gloss inventory (source recorded).
2. Demonstrate ambiguity honestly: at least one example where the same word has different senses in context and the
   chosen sense changes the translation/entity result — stored as a test case.
3. Do not over-claim: if WSD rarely changes outputs in the tourism domain, that is the finding; record coverage
   (how often WSD fired) alongside impact (how often it changed results).
4. WSD must not be forced into the translation path where it adds nothing (same principle as E6 below).

## 11. N-gram rules (and E6 POS policy)

1. N-gram counts are built **only** from the actual preprocessed corpus; hardcoded probability tables are
   forbidden.
2. The smoothing method chosen (e.g., add-k, Kneser-Ney — **DECISION REQUIRED** at Phase 7) is recorded with the
   rationale.
3. The n-gram model is a **baseline/reference** (FR-12), not a claimed improvement over the MT pipeline.
4. **E6 (HMM/Viterbi/POS):** build it only if a concrete use is identified (e.g., features for chunking or WSD
   context). If it provides no useful functionality in this project, document that conclusion with evidence and
   leave it out of the pipeline — do not force it into translation. Whichever outcome, the E6 status in
   `Memory.md` states exactly what exists and works.

## 12. Evaluation rules

1. Metrics (PRD §12): BLEU (sacrebleu preferred, NLTK BLEU fallback — record which), chrF if available,
   exact/acceptable match on curated tourist phrases, category accuracy, NER precision/recall/F1, response time.
2. Metric configuration is part of the result: tokenizer, casing, smoothing, corpus concatenation method — all
   recorded next to numbers.
3. Evaluation runs only on frozen test sets; first run's configuration is the reference configuration.
4. Response times: define the measured region (e.g., model inference only vs end-to-end) before measuring; record
   hardware (CPU/GPU/RAM) and repetition count.
5. All numbers land in `Memory.md` § Evaluation and the final report with their date and configuration; superseded
   results are marked, not deleted.
6. **No invented numbers** — if a metric was not run, it stays **NOT YET CALCULATED**.

## 13. Error handling

1. User-facing failures produce clear states in the UI (empty input, script/direction mismatch, model unavailable,
   internal error) per `Design.md` §10 — never a fabricated success.
2. Scripts (`scripts/run_*.py`) exit non-zero on failure and print the actual cause; silent catch blocks that
   mask failures are forbidden in pipelines and evaluation code.
3. Download/load steps verify what they got (file exists, loads, correct language tags) before use.
4. Errors encountered in real runs are logged and, if they persist, recorded in `Memory.md` § Known Issues.
5. Degrade explicitly: if a component (WSD, POS, chrF) cannot run, the pipeline states it was skipped and why —
   results are never silently padded.

## 14. AI coding assistant rules

Binding for every AI-assisted change (this repository is regularly driven by AI coding sessions):

- **Inspect existing code before editing.** Read the module and its tests first; follow existing style.
- **Do not rewrite working modules unnecessarily.** Refactor only with cause; preserve behavior.
- **Make one logical change at a time.** No drive-by edits outside the task.
- **Run validation after changes** — the relevant tests (§15) must pass before a change is called done.
- **Do not invent files, APIs, dataset columns, or model outputs.** If it is not in the repo or docs, ask or look.
- **Do not claim an experiment is implemented unless it actually works** (run it, show it).
- **Maintain `Memory.md` after implementation begins** — update after every major completed phase.
- **Preserve reproducibility** — fixed seeds, documented commands, no hidden state.
- AI sessions must not alter frozen test sets or backdate results; documentation edits keep markers (NOT YET
  CALCULATED / DECISION REQUIRED / ASSUMPTION) accurate.

## 15. Testing rules

1. Test framework: Python stdlib **`unittest`** (no added dependency), suites under `tests/` mirroring `src/`.
2. Minimum suites: Unicode round-trip tests (E1/§5), preprocessing golden tests (E2), regex pattern tests (E3),
   n-gram count/prediction tests against a tiny hand-computed fixture (E4), transliteration round-trip tests (§6),
   pipeline routing tests for D1–D4, evaluation smoke test on a toy pair set.
3. Expected values in tests are **hand-computed from small fixtures**, never copied from implementation output.
4. Tests run offline with no network and no large model download (model-dependent tests are marked/skipped when
   the model is absent).
5. Determinism: generators/seeds fixed; tests must pass repeatedly and on clean checkouts.
6. New functionality ships with its tests; a phase is not "validated" without the checks listed in `Phases.md`.

## 16. Documentation rules

1. Documentation files (`PRD.md`, `Architecture.md`, `Rules.md`, `Phases.md`, `Design.md`, `Memory.md`) must stay
   internally consistent; when a decision changes, update every affected file in the same change.
2. `Memory.md` is the source of truth for *state* (what exists, what was measured); docs are the source of truth
   for *intent* (what should exist). Conflicts → reconcile immediately and note it in `Memory.md` § Last Updated.
3. Update `Memory.md` after every major completed phase: Current Phase, Completed Work, Files, Commands,
   Evaluation, Last Updated.
4. Mark future/unverified items as **planned**; never delete a failed-attempt record — annotate it.
5. Keep tables/lists factual: no aspirational statuses like "almost done" — statuses are done (tested) / in
   progress / not started.
6. Report and slide numbers are copied from `Memory.md` only.

---

*These rules are enforced through the phase validation criteria in `Phases.md` and the test suite (§15).*
