# Phases — Malayalam Tourist Translation & Transliteration System

| | |
|---|---|
| **Status** | Plan only — no phase has started (see `Memory.md` § Current Phase) |
| **Created** | 2026-09-30 |
| **Rule** | A phase may not start until every item in its **Dependencies** is available and validated. Phase order below is the default sequence; where phases are marked independent they may run in parallel **after** their dependencies are met. |

**Per-phase fields:** Objective · Tasks · Files/modules affected · Expected output · Validation criteria · Dependencies.

Markers: **planned** = not built · **NOT YET CALCULATED** = not yet measured · **DECISION REQUIRED** = unresolved choice.

---

## Phase 1 — Project setup

- **Objective:** Establish a clean, runnable, reproducible Python project skeleton with documentation and version control ready.
- **Tasks:**
  1. Verify the repo contains the six docs (`PRD.md`, `Architecture.md`, `Rules.md`, `Phases.md`, `Design.md`, `Memory.md`) and `AGENTS.md`.
  2. Create the folder skeleton: `src/` (per `Architecture.md` §14), `tests/`, `scripts/`, `reports/`, `data/` (empty subdirs `raw/ processed/ tourism/ test/`), `models/`, `notebooks/` (optional).
  3. Write `.gitignore` (exclude `models/`, `data/raw/`, `data/processed/`, `reports/*.png`, `__pycache__/`, `.venv/`; **keep** `data/test/`, `data/tourism/` curated small files).
  4. Create a virtual environment; install the `Architecture.md` §12 stack only (Python, Pandas, NLTK, spaCy *if used*, Hugging Face Transformers, PyTorch, Streamlit, Matplotlib, SacreBLEU).
  5. Add `src/config.py` with shared constants (paths, 8 tourism categories, language tags, seed).
  6. Add `tests/test_smoke.py` and `scripts/run_smoke.py`; record exact setup commands.
- **Files/modules affected:** `src/` (new), `tests/` (new), `scripts/` (new), `data/` (new, empty), `models/` (new, gitignored), `.gitignore`, `Memory.md`.
- **Expected output:** Empty-but-importable package layout; `python -m unittest` runnable; env installs cleanly from documented commands.
- **Validation criteria:** `python -c "import src.config"` succeeds; `python -m unittest` passes the smoke test; `git status` shows no large/binary artifacts; setup commands verified by running them exactly as documented.
- **Dependencies:** All six documentation files complete (this documentation phase).

---

## Phase 2 — Dataset collection

- **Objective:** Acquire the four dataset classes legally and record verified facts about each.
- **Tasks:**
  1. Evaluate candidate sources (AI4Bharat **Samanantar**, **BPCC**, tourism-domain parallel data, Manglish–Malayalam pairs); check each license before download.
  2. Download into `data/raw/<source>/` (immutable).
  3. For each accepted dataset record in `Memory.md` § Dataset: name, source URL, license, **actual counted** sentence pairs, format, known quality issues.
  4. Build the frozen test sets `data/test/d1..d4/` (curated tourist phrases incl. the spec reference triplet; direction coverage per `PRD.md` §6–7) — freeze from this point.
  5. Record rejected candidates and why (evidence of diligence).
- **Files/modules affected:** `data/raw/**`, `data/test/**`, `Memory.md` (§ Dataset, § Decisions).
- **Expected output:** Raw corpora on disk + a fully filled dataset record table; frozen test sets committed.
- **Validation criteria:** Every collected dataset has all six recording fields populated with **counted** numbers (no estimates); licenses permit academic use; raw files hash-stable/unchanged after commit; test sets cover all 4 directions and all 8 categories at least once (counts recorded, not assumed).
- **Dependencies:** Phase 1 (folders + `.gitignore` exist).

---

## Phase 3 — Dataset cleaning

- **Objective:** Turn raw data into validated `data/processed/` corpora without touching raw or test data.
- **Tasks:**
  1. Implement deduplication, language/script filtering (reject wrong-script pairs), length filtering, empty/mismatched-pair removal, encoding repair.
  2. Produce cleaning statistics (before/after counts per dataset) — **counted** values.
  3. Persist cleaned data as UTF-8 files under `data/processed/` mirroring the raw tree.
  4. Write cleaning report (`reports/cleaning_report.md` or `.csv`).
- **Files/modules affected:** `src/preprocessing/clean.py`, `scripts/run_clean.py`, `data/processed/**`, `reports/`.
- **Expected output:** Processed corpora + counted cleaning statistics.
- **Validation criteria:** Re-running cleaning is idempotent (same output hash); `data/raw/` untouched; stats table matches file line counts when verified by an independent count command; no test-set text appears in processed corpora (grep check).
- **Dependencies:** Phase 2 (raw data exists).

---

## Phase 4 — Text preprocessing

- **Objective:** Build the shared preprocessing pipeline (course Experiments 1 + 2) that every later module reuses.
- **Tasks:**
  1. `src/preprocessing/text_ops.py` (E1): Unicode NFC normalization, whitespace ops, split/join/replace, word counting, case handling for English/Manglish, Malayalam preservation helpers.
  2. `src/preprocessing/tokenizer.py` (E2): Malayalam-aware tokenization, punctuation/whitespace normalization, filtering with `mode="translation"` vs `mode="corpus"`.
  3. Golden tests: hand-written input/output pairs (EN, ML, Mg, mixed-script, edge cases: chillra clusters, ZWJ, emoji, URLs).
  4. Unicode round-trip tests (`Rules.md` §5).
- **Files/modules affected:** `src/preprocessing/*`, `tests/test_text_ops.py`, `tests/test_tokenizer.py`.
- **Expected output:** Importable, tested preprocessing API documented with its tokenization/counting definitions.
- **Validation criteria:** All E1/E2 unit tests pass; round-trip identity holds for Malayalam fixtures; identical sentence processed by two modules yields identical tokens (cross-module consistency test); definitions (word = ?, grapheme = ?) recorded in `Memory.md`.
- **Dependencies:** Phase 1 (skeleton); Phase 3 outputs to process (clean data available).

---

## Phase 5 — Regex processing

- **Objective:** Build the E3 pattern library for tourism-relevant numeric/special patterns.
- **Tasks:**
  1. `src/patterns/regex.py`: patterns for prices, currency amounts (₹/INR/Rupees variants), phone numbers, numbers/ordinals, URLs, times/dates — EN + ML digits.
  2. Unit tests per pattern with positive **and** negative fixtures (hand-written).
  3. Extraction API returning spans + labels, ready for the NER merge layer.
- **Files/modules affected:** `src/patterns/regex.py`, `tests/test_regex.py`.
- **Expected output:** Compiled, documented pattern library with tested extraction.
- **Validation criteria:** Every pattern has passing positive/negative tests; no false match on the negative fixture set; extraction spans verified manually on a small sample (≥20 sentences, spot-check documented).
- **Dependencies:** Phase 4 (text ops available for span handling).

---

## Phase 6 — EDA / Word Cloud

- **Objective:** Understand the tourism corpus (course Experiment 8) and produce report artifacts.
- **Tasks:**
  1. `src/eda/stats.py`: word/char frequency (per language), type/token ratio, hapax, sentence-length distributions, vocabulary analysis, category distribution (once category labels exist).
  2. `src/eda/wordcloud.py`: word clouds for English and Malayalam (font handling per `Design.md` §13).
  3. `scripts/run_eda.py` → figures/tables in `reports/`.
  4. Suggest additional EDA techniques in the report (spec requirement: *suggest*, not fabricate results for).
- **Files/modules affected:** `src/eda/*`, `scripts/run_eda.py`, `reports/`.
- **Expected output:** Reproducible EDA artifacts from the real processed corpus.
- **Validation criteria:** Figures render **no missing-glyph (tofu) boxes** for Malayalam (visual check documented); stats tables reproduce exactly on re-run; every number in the report traces to `reports/` outputs; nothing from `data/test/` included.
- **Dependencies:** Phases 3 + 4 (processed corpus + preprocessing).

---

## Phase 7 — N-gram baseline

- **Objective:** Build the E4 bigram/trigram model as a language-model baseline (FR-12).
- **Tasks:**
  1. `src/ngram/builder.py`: bigram/trigram counts from preprocessed corpus (raw counts stored/computed, no hardcoded probabilities).
  2. Choose and record smoothing (**DECISION REQUIRED**: add-k vs Kneser-Ney) with rationale → `Memory.md` § Decisions.
  3. `src/ngram/predictor.py`: next-word prediction API + a tiny demo script.
  4. Tests against a hand-computed toy corpus fixture (probabilities computed by hand in the test).
- **Files/modules affected:** `src/ngram/*`, `scripts/run_ngram_demo.py`, `tests/test_ngram.py`, `Memory.md` (§ Decisions).
- **Expected output:** Working next-word prediction over the tourism corpus + recorded smoothing decision.
- **Validation criteria:** Toy-fixture probabilities match hand-computed values; prediction on corpus sentences returns sensible top-k (manual inspection logged); rebuild from scratch reproduces identical counts.
- **Dependencies:** Phase 4.

---

## Phase 8 — NER / Chunking

- **Objective:** Implement entity extraction (E5 + E3) and the tourism category detector with measured quality (FR-5, FR-6).
- **Tasks:**
  1. `src/ner/chunker.py`: noun-phrase chunking (Malayalam + English; spaCy *where appropriate* per `Architecture.md` §12).
  2. `src/ner/extractor.py`: merge regex layer (Phase 5) + chunk layer into typed entities (PRD FR-6 types); decide and record merge priority (**DECISION REQUIRED**).
  3. Create a hand-labeled evaluation sample (labeling process documented: size, labeler, guidelines) — kept held-out.
  4. Category detection baseline (keyword/rule-based) in `src/pipeline/` or `src/ner/` (location decided in this phase, recorded).
  5. Precision/recall/F1 computation wired into `src/evaluation/`.
- **Files/modules affected:** `src/ner/*`, category detector module, `data/tourism/` or `data/test/ner_labels/`, `src/evaluation/metrics.py`, `tests/test_ner.py`, `Memory.md` (§ Decisions).
- **Expected output:** Entity + category extraction that outputs typed lists; first **measured** P/R/F1 and accuracy (recorded as measured, with date/config).
- **Validation criteria:** Hand-labeled sample exists and is frozen; P/R/F1 computed from an actual run and recorded in `Memory.md` (no claims without numbers); merge policy documented before scoring; unit tests for each entity type pass.
- **Dependencies:** Phases 4 + 5 (preprocessing + regex); Phase 2 (data to label).

---

## Phase 9 — WSD

- **Objective:** Implement Lesk-style WSD (E7) for tourism-relevant ambiguity and demonstrate its effect on translation/entity output.
- **Tasks:**
  1. `src/wsd/lesk.py`: signature/gloss inventory (source recorded, e.g., WordNet-style); overlap scoring over the sentence context.
  2. Curate ambiguity demonstration cases (same word, ≥2 senses, tourism context) as tests — e.g., *room* (hotel vs living room), *charge* (fee vs battery), *bank* (financial vs river).
  3. Measure: coverage (how often WSD fires) and impact (how often the chosen sense changes a downstream result) — **NOT YET CALCULATED** until run.
  4. Decide integration point: WSD before NER/translation (record decision; integration may be a no-op if impact ≈ 0 — report honestly).
- **Files/modules affected:** `src/wsd/*`, `tests/test_wsd.py`, `Memory.md` (§ Decisions, later § Evaluation).
- **Expected output:** Working WSD module + ambiguity demo cases + measured coverage/impact.
- **Validation criteria:** Demo cases resolve to the contextually correct sense in tests; coverage/impact numbers measured from real runs (or explicitly **NOT YET CALCULATED**); gloss inventory source documented.
- **Dependencies:** Phase 4 (context extraction); Phase 8 useful first (entity context for ambiguous words).

---

## Phase 10 — Translation engine

- **Objective:** Stand up the pretrained MT engine (candidate: IndicTrans2) for direct directions D1/D2.
- **Tasks:**
  1. Research/confirm checkpoint (English ↔ Malayalam support); record in `Memory.md` § Model: name, version/revision, source URL, license, language codes/tags, download date — **only after actual download**.
  2. Download to `models/` (gitignored); document the exact command in `Memory.md` § Commands.
  3. `src/translation/engine.py`: load model, translate(text, src, tgt), graceful failure if model absent (`Rules.md` §4/§13).
  4. `src/translation/postprocess.py`: whitespace/punctuation restoration, script sanity check (output script matches expected target script).
  5. Smoke test: translate the 3 spec reference sentences (EN→ML, ML→EN) and **observe** outputs — record examples as *observed model output* with date, not as promised quality.
- **Files/modules affected:** `src/translation/*`, `models/` (downloaded), `scripts/run_translate_smoke.py`, `tests/test_engine.py` (skippable if model absent), `Memory.md` (§ Model, § Commands).
- **Expected output:** Working D1/D2 translation callable + model provenance recorded.
- **Validation criteria:** Model loads offline; reference sentences translate without exceptions and outputs pass script sanity check; failure path (rename model dir → error state, no fabricated output) tested; `Memory.md` § Model fully populated with **verified** fields; never claims team training.
- **Dependencies:** Phase 4 (preprocessing in front of model); Phase 1 (stack incl. Transformers/PyTorch installed).

---

## Phase 11 — Manglish transliteration/normalization

- **Objective:** Build Malayalam ↔ Manglish conversion with one standard scheme (E1/E2 application; PRD D3/D4 building block).
- **Tasks:**
  1. Decide the **standard Manglish scheme** (**DECISION REQUIRED**: ITRANS-like vs ISO-15919-like vs corpus-dominant style) → `Memory.md` § Decisions.
  2. `src/transliteration/ml_to_mg.py`: Malayalam → Manglish (script-level romanization).
  3. `src/transliteration/mg_to_ml.py`: Manglish → Malayalam normalization (lowercase, whitespace, variant folding → Malayalam) for route D3.
  4. Tests: round-trip on curated pairs (`Mg → Ml → Mg` stability measured and reported honestly); spec triplet as fixtures.
  5. If a Manglish–Malayalam paired dataset was collected (Phase 2), use it for measured round-trip accuracy.
- **Files/modules affected:** `src/transliteration/*`, `tests/test_transliteration.py`, `data/` (paired data use), `Memory.md` (§ Decisions).
- **Expected output:** Tested Ml↔Mg conversion + recorded scheme decision.
- **Validation criteria:** Round-trip results measured and recorded (expected imperfect — actual numbers only); "Enikku oru taxi venam." normalizes to a Malayalam string that feeds D2 correctly; scheme decision recorded before implementation completes.
- **Dependencies:** Phase 4.

---

## Phase 12 — Four-direction translation pipeline

- **Objective:** Compose D1–D4 exactly as specified and expose them as one routing API (FR-1..FR-4).
- **Tasks:**
  1. `src/pipeline/directions.py`: route table — D1: preprocess→MT→post; D2: same; D3: Mg→Ml→preprocess→MT→post; D4: preprocess→MT→Ml→Mg→post.
  2. Attach side outputs: category (Phase 8), entities (Phase 8), WSD flags (Phase 9, if integrated).
  3. End-to-end tests for all 4 directions using spec reference sentences (assert pipeline runs + output sanity, **not** exact-match quality claims unless measured).
  4. Response-time instrumentation (start/end timing per call) ready for Phase 13.
- **Files/modules affected:** `src/pipeline/directions.py`, `tests/test_directions.py`, `src/evaluation/timing.py`.
- **Expected output:** Single `translate(direction, text)` API working end-to-end for D1–D4.
- **Validation criteria:** All 4 direction tests pass offline (with model present); routes match `Architecture.md` §4–5 exactly (code review against doc); empty/wrong-script inputs produce defined errors, never fabricated text.
- **Dependencies:** Phase 10 (MT engine), Phase 11 (transliteration); Phases 8–9 outputs available for side outputs (may land as optional attachments).

---

## Phase 13 — Evaluation

- **Objective:** Produce all measured metrics required by PRD §12/§16 on frozen test sets.
- **Tasks:**
  1. **Pre-register thresholds** for SC-2..SC-6 (numeric targets decided *before* runs — **DECISION REQUIRED**) → `Memory.md`.
  2. Freeze/verify test sets (`data/test/`); record their sizes (counted).
  3. `src/evaluation/bleu.py`: BLEU via SacreBLEU (preferred) / NLTK fallback — record which; chrF if available.
  4. `src/evaluation/metrics.py`: exact/acceptable match (curated tourist phrases), category accuracy, NER P/R/F1.
  5. `src/evaluation/timing.py`: response time per direction (defined measurement region, hardware noted, N repetitions).
  6. `scripts/run_eval.py` → `reports/evaluation_<date>.md|csv`; write **actual numbers** into `Memory.md` § Evaluation with date + config.
  7. Baseline comparison: n-gram baseline (Phase 7) referenced in the discussion.
- **Files/modules affected:** `src/evaluation/*`, `scripts/run_eval.py`, `reports/`, `Memory.md` (§ Evaluation, § Decisions).
- **Expected output:** Evaluation report with measured BLEU/(chrF)/exact-match/accuracy/F1/response-time for all applicable directions.
- **Validation criteria:** Every reported number reproducible by one documented command; config + hardware recorded alongside; no **NOT YET CALCULATED** left where a run was possible; no number invented (self-audit against `Rules.md` §3); frozen test sets unmodified (hash check vs Phase 2).
- **Dependencies:** Phase 12 (pipeline), Phase 2 (frozen test sets), Phases 8–9 (accuracy/F1 metrics), Phase 7 (baseline for comparison).

---

## Phase 14 — UI

- **Objective:** Implement the Streamlit interface per `Design.md` (FR-7, FR-8, FR-9).
- **Tasks:**
  1. `src/ui/app.py`: direction selector (4 options), input area, Translate button, output panel, detected category, entity display, error/loading states per `Design.md` §10–11.
  2. Wire to `src/pipeline/directions.py` only (UI contains no NLP logic).
  3. Malayalam/Manglish rendering per `Design.md` §13–14; responsive layout §12; accessibility labels §15.
  4. Manual test script: the 4 reference sentences, empty input, wrong-script input, model-missing scenario.
- **Files/modules affected:** `src/ui/app.py`, `scripts/run_app.py`, `tests/test_ui_helpers.py` (pure helpers only), `Design.md` (any discrepancy notes).
- **Expected output:** Launchable UI (`streamlit run`) demonstrating all four directions with category + entities.
- **Validation criteria:** Manual test script passes all cases incl. failure states; UI has zero NLP logic (review); Malayalam displays correctly (visual check, no tofu); `streamlit run` launches from documented command.
- **Dependencies:** Phase 12 (pipeline API), Phase 1 (Streamlit installed), `Design.md` (spec exists from documentation phase).

---

## Phase 15 — Integration

- **Objective:** Assemble the complete system: UI + pipeline + all side components + reports as one coherent app.
- **Tasks:**
  1. Full wiring check: preprocessing shared everywhere; NER/category/WSD/N-gram integrated where decided; no duplicate cleaners (`Rules.md` §8).
  2. `scripts/run_app.py` / `run_eval.py` / `run_eda.py` entry points documented end-to-end in `Memory.md` § Commands (verified by executing).
  3. First full demo run: 8 categories × 4 directions = 32 sanity sentences through the UI (results observed, anomalies logged).
  4. `Memory.md` full update (Current Phase, Files, Commands, Decisions).
- **Files/modules affected:** `src/pipeline/*`, `src/ui/app.py`, `scripts/*`, `Memory.md`.
- **Expected output:** One-command app launch + verified command documentation + integration findings logged.
- **Validation criteria:** 32-sentence demo completes without crashes; all documented commands executed verbatim successfully; component inventory matches `Architecture.md` §2 (or doc updated in same change).
- **Dependencies:** Phases 12 + 14 (and 8/9 integrations as decided).

---

## Phase 16 — Testing

- **Objective:** Full regression + robustness pass before the final report.
- **Tasks:**
  1. Complete `tests/` suites per `Rules.md` §15; ensure clean-checkout run (clone → setup → `python -m unittest`) works.
  2. Edge-case battery: mixed scripts, very long input, empty/whitespace, emoji, HTML/script tags, all-Malayalam input in D1, all-English in D2, wrong-script Manglish, unicode edge cases (ZWJ, combining marks).
  3. Performance sanity: response times re-measured (consistency with Phase 13; drift investigated and logged).
  4. Bug fixing: one logical fix per change, each covered by a new/updated test (`Rules.md` §14).
- **Files/modules affected:** `tests/**`, bug-fix touches across `src/`, `Memory.md` (§ Known Issues).
- **Expected output:** Passing test suite from clean checkout; documented edge-case results; known issues list current.
- **Validation criteria:** `python -m unittest` all-green on clean checkout using only documented commands; every edge case has a defined (non-crashing, non-fabricating) behavior; no open critical bugs (list in `Memory.md`).
- **Dependencies:** Phase 15 (integrated system), Phase 13 (perf baseline for comparison).

---

## Phase 17 — Documentation and final presentation

- **Objective:** Finalize all documentation/report with measured results and prepare the presentation.
- **Tasks:**
  1. Update all six docs for any implementation-phase decisions (consistency pass, `Rules.md` §16).
  2. Final report: overview → experiments E1–E8 contributions → architecture → datasets (verified table) → results (copy **only** from `Memory.md` § Evaluation) → limitations → future work.
  3. Slides/demo script: live UI demo, ambiguity (WSD) demonstration case, word cloud, sample translations, honest metric discussion.
  4. Verify every claim in the report against the repo (a claim without a traceable artifact is removed or marked **planned**).
  5. `Memory.md` final update (Last Updated + change list).
- **Files/modules affected:** All `.md` files, `reports/`, presentation artifacts.
- **Expected output:** Internally consistent final documentation + report + presentation using only measured numbers.
- **Validation criteria:** Report numbers == `Memory.md` numbers; every experiment E1–E8 has an explicit status (implemented+measured / evaluated-but-not-adopted with reason / not applicable with reason); no fabricated data anywhere; docs pass consistency review.
- **Dependencies:** Phase 13 (results exist), Phase 16 (tests pass).

---

## Dependency summary

```
1 ─► 2 ─► 3 ─► 4 ─┬► 5 ─► 8 ─► 9 ─┐
                   ├► 6              │
                   ├► 7              ├► 12 ─► 13 ─► (14 ─► 15) ─► 16 ─► 17
                   ├► 10 ────────────┤              ▲
                   └► 11 ────────────┘              └ (13 needs 12, 2, 7, 8, 9)
```

- No phase begins before its dependencies are validated (top of file, hard rule).
- Phases 5, 6, 7, 10, 11 are mutually parallel after Phase 4.
- Phases 8, 9 follow 5; Phase 9 may follow 8 or run parallel to it after Phase 5.
- Evaluation (13) requires: frozen test sets (2), working four-direction pipeline (12), measured components (7, 8, 9).

*Plan only — statuses live in `Memory.md`. Never mark a phase complete until its validation criteria have actually been executed.*
