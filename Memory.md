# Memory — Persistent Project Context

> This file is the source of truth for **project state** for future AI coding sessions.
> Update it after every major completed phase.
> **Never claim something is completed until it has been tested.**
> Markers: **NOT YET CALCULATED** = not yet computed · **DECISION REQUIRED** = unresolved ·
> **ASSUMPTION** = unverified guess · **planned** = specified but not implemented.

---

## Project

**Malayalam Tourist Translation & Transliteration System** — a college NLP mini-project: a tourism-focused
translation & transliteration application for Kerala supporting four directions (English ↔ Malayalam,
Manglish → English, English → Manglish), combining a **pretrained** multilingual translation model with the
course NLP experiments (string processing, preprocessing, regex, n-grams, chunking/NER, HMM/Viterbi POS, WSD,
word cloud/EDA). Manglish is treated as **Romanized Malayalam**, never as an independent language.

Authoritative spec: `New Text Document.txt`. Intent docs: `PRD.md`, `Architecture.md`, `Rules.md`, `Phases.md`,
`Design.md`. This file = current state. Onboarding entry point for humans and agents: `README.md`.

## Team

- Ronald Aaron Tamil Arasan
- Sharon Sam
- Sam Manoj

## Translation Directions

| ID | Direction | Status |
|---|---|---|
| D1 | English → Malayalam | **implemented (tested)** — pretrained inference works end-to-end (measured 2026-09-30: correct outputs, 0.37 s/sentence, CPU, beam 5). Not yet exposed via `src/translation.py` (`src/` not created). |
| D2 | Malayalam → English | **in progress** — checkpoint loads; weights measure clean; `generate()` returns junk ("to"); **open KNOWN ISSUE**, diagnosis started (see Known Issues; details in `docs/MODEL.md`) |
| D3 | Manglish → English (via Malayalam normalization → D2) | **planned** (not started; blocked by D2) |
| D4 | English → Manglish (via D1 → Malayalam→Manglish transliteration) | **planned** (not started) |

## NLP Experiments

| # | Experiment | Status | Notes |
|---|---|---|---|
| 1 | String Processing | not started | Planned: `src/preprocessing/text_ops.py` (Phase 4) |
| 2 | Text Preprocessing | not started | Planned: `src/preprocessing/tokenizer.py`, `clean.py` (Phase 4) |
| 3 | Regular Expressions | not started | Planned: `src/patterns/regex.py` (Phase 5) |
| 4 | N-gram (bigram/trigram, next-word) | not started | Planned: `src/ngram/` (Phase 7); smoothing = **DECISION REQUIRED** |
| 5 | Chunking | not started | Planned: `src/ner/chunker.py` (Phase 8) |
| 6 | NER | not started | Planned: `src/ner/extractor.py` (Phase 8); merge policy = **DECISION REQUIRED** |
| 7 | HMM / Viterbi / POS | not started | Policy: build **only if useful**; if not adopted, document why (`Rules.md` §11) |
| 8 | WSD (Lesk-style) | not started | Planned: `src/wsd/lesk.py` (Phase 9) |
| 9 | Word Cloud / EDA | not started | Planned: `src/eda/` (Phase 6) |

Status values used: `not started` / `in progress` / `implemented (tested)` / `evaluated but not adopted (reason)`.

## Dataset

**Raw shard downloaded and verified (2026-09-30). Splits and tourism set NOT YET CREATED.**

| Field | Value (measured / verified 2026-09-30) |
|---|---|
| Name | AI4Bharat Samanantar |
| Source (URL) | https://huggingface.co/datasets/AI4Bharat/Samanantar |
| License | CC-BY-NC-4.0 |
| Config / split | `ml` config; `train` split only (dataset publishes no val/test) |
| Sentence pairs (counted) | **1,481,107 rows** in the downloaded shard (pandas count); 5,924,426 pairs in `ml` total (HF API-reported, all 4 shards) |
| Downloaded | shard 0 only: `data/raw/samanantar/train-00000-of-00004.parquet`, **196,182,916 bytes** (identical to HF API-reported size) |
| Columns | `idx` (int64), `src` (str, English), `tgt` (str, Malayalam) |
| Preprocessing applied | none yet (`data/raw/` is immutable) |
| Train/val/test split | **NOT YET CREATED** (plan: 80/10/10, seed 42 → `data/processed/`, no cross-split duplicates) |

- Full record + reproducible download command: `docs/DATASET.md`.
- Required classes: general EN–ML (Samanantar, above) · tourism-specific EN–ML **NOT YET CREATED** ·
  Manglish–ML pairs = **DECISION REQUIRED** (source not chosen) · test sets for D1–D4.
- Layout: `data/raw/ processed/ tourism/ test/` — raw never overwritten; `data/` gitignored (100 MB GitHub limit).

## Model

| Field | Value |
|---|---|
| Model name | IndicTrans2 `dist-200M` checkpoints (pretrained) |
| Status | D1 tested via `scripts/smoke_translate.py`; D2 open known issue (diagnosis started); `src/translation.py` **not created** |
| Version / checkpoint | EN→ML: mirror `naklitechie/indictrans2-en-indic-dist-200M`; ML→EN: weights `Raghavan/indictrans2-indic-en-dist-200M` + tokenizer/config `hari31416/indictrans2-indic-en-dist-200M-ONNX` (official `ai4bharat/*` gated: HTTP 401, no HF token on this machine) |
| Measured params | EN→ML 274,584,576 · ML→EN 228,316,160 (counted from loaded models; both match official counts) |
| License | MIT (model cards) |
| Language codes/tags | `eng_Latn` ↔ `mal_Mlym` (the model's own FLORES-200 tags, prepended by IndicProcessor) |
| Pretrained or fine-tuned | **Pretrained** — no training or fine-tuning performed; `src/train.py` intentionally absent |

- Provenance, re-download commands, transformers-v5 patch list, smoke outputs: `docs/MODEL.md`.
- Patches applied by `scripts/patch_model_files.py` (transformers 5.12.1 vs 4.x-era checkpoint code; idempotent).
- Preprocessing component vendored at `vendor/IndicTransToolkit/` (pip install fails on Windows) — provenance in its README.
- The team does **not** claim to have trained this model.

## Current Phase

**Environment + data + model setup done; D1 inference implemented and tested; D2 diagnosis in progress.**
`src/` modules, dataset splits, tourism set, baselines, evaluation, notebooks, UI: **not created**.
Next per `Phases.md`: resolve the D2 KNOWN ISSUE (README next-steps #1), then create `src/`
(config → preprocessing → translation), then seeded sampling/splits.

## Completed Work

Only what exists and is verified:

- [x] Project documentation created: `PRD.md`, `Architecture.md`, `Rules.md`, `Phases.md`, `Design.md`, `Memory.md`, `AGENTS.md` (2026-09-30).
- [x] Project spec available as `New Text Document.txt` (authoritative).
- [x] Onboarding docs created: `README.md`, `requirements.txt`, `.gitignore`, `docs/DATASET.md`, `docs/MODEL.md`, `vendor/IndicTransToolkit/README.md` (2026-09-30).
- [x] Environment measured and pinned: Python 3.13.5; torch 2.12.0 (CPU), transformers 5.12.1, pandas 2.2.3, numpy 2.3.3, nltk 3.10.3, sentencepiece 0.2.2, sacrebleu 2.6.0, sacremoses 0.2.0, indic-nlp-library-itt 0.1.1, pyarrow 25.0.0, matplotlib 3.10.8, streamlit 1.59.1.
- [x] Samanantar `ml` shard 0 downloaded and verified (byte size matches HF API; row count measured).
- [x] Both checkpoints downloaded; parameter counts measured; raw weight scan clean (0 NaN/Inf, max |w| ≤ 10).
- [x] IndicTransToolkit vendored (pure-Python port, provenance + `vendor/pyx_to_py.py` recorded).
- [x] `scripts/patch_model_files.py` created and run (idempotent, both checkpoints patched).
- [x] `scripts/smoke_indicprocessor.py` — **PASSED** (EN/ML preprocess + postprocess round-trip).
- [x] `scripts/smoke_translate.py enml` — **PASSED** (3 correct Malayalam outputs; 1.1 s / 3 sentences → 0.37 s/sentence, CPU beam 5; recorded in `docs/MODEL.md`).
- [x] D2 diagnostics created and run (2026-09-30): `diagnose_ml_en.py`, `probe_ml_en_inputs.py`, `probe_ml_en_encoder.py`, `probe_ml_en_weights.py` — findings recorded in `docs/MODEL.md` § KNOWN ISSUE.

**Nothing else is implemented.** No `src/`, no splits, no baselines, no evaluation, no notebooks, no UI.

## In Progress

- D2 ML→EN known-issue diagnosis (measured findings in `docs/MODEL.md` § KNOWN ISSUE).
  Next step **NOT YET RUN**: end-to-end retest with `low_cpu_mem_usage=False`.

## Pending

- Resolve D2 KNOWN ISSUE, then Phases of `Phases.md` in dependency order (`src/` → datasets/splits →
  preprocessing → E1–E8 components → translation engine → transliteration → four-direction pipeline →
  evaluation → UI → integration → testing → final docs/presentation).
- All functional/NLP requirements in `PRD.md` beyond D1 inference are **planned**.
- Git: execute and verify the push sequence (`.gitignore` now exists; still required: untrack >100 MB files,
  commit, reconcile with remote `origin/main`, push) — Part 20 safety rules apply (status/diff/log before and after).

## Decisions

| # | Decision | Reason | Date |
|---|---|---|---|
| 1 | Docs-first: only the 6 documentation files before any code | Spec requirement; docs must be internally consistent first | 2026-09-30 |
| 2 | Manglish = Romanized Malayalam, always routed through Malayalam (D3/D4) | Spec: never an independent language | 2026-09-30 |
| 3 | Translation via a **pretrained** model; IndicTrans2 family as candidate | Supports EN↔ML; training from scratch out of scope | 2026-09-30 |
| 4 | Fixed stack: Python, Pandas, NLTK, spaCy (where appropriate), HF Transformers, PyTorch, Streamlit, Matplotlib, SacreBLEU/NLTK BLEU; stdlib `unittest` for tests | Spec: no unnecessary technologies | 2026-09-30 |
| 5 | Documentation lives at repo root; code in `src/`, tests in `tests/`, scripts in `scripts/` | Matches `Architecture.md` §14 | 2026-09-30 |
| 6 | E6 (HMM/Viterbi/POS) only adopted if it demonstrably helps; otherwise documented as evaluated-but-not-adopted | Spec: do not force it into translation | 2026-09-30 |
| 7 | Markers NOT YET CALCULATED / DECISION REQUIRED / ASSUMPTION used everywhere | No fabricated data rule | 2026-09-30 |
| 8 | Manglish romanization scheme (ITRANS-like vs corpus-dominant) | **DECISION REQUIRED** at Phase 11 | — |
| 9 | NER regex/chunk merge priority; category-detection module location | **DECISION REQUIRED** at Phase 8 | — |
| 10 | N-gram smoothing method | **DECISION REQUIRED** at Phase 7 | — |
| 11 | Pre-registered numeric success thresholds | **DECISION REQUIRED** at Phase 13 (before runs, not after) | — |
| 12 | Use ungated HF mirrors for IndicTrans2 (official repos gated, HTTP 401, no HF token here) | Reproducible downloads; param counts verified against official | 2026-09-30 |
| 13 | Vendor IndicTransToolkit as a pure-Python port instead of pip install | Windows: no wheels, MSVC unavailable; WSL rejected to keep one environment | 2026-09-30 |
| 14 | Handle transformers 5.12.1 via `scripts/patch_model_files.py`, not a downgrade | Keeps global env; patch is idempotent, reviewable, inference-neutral | 2026-09-30 |
| 15 | pandas + pyarrow instead of the HF `datasets` package | Fewer dependencies; reading parquet is trivial | 2026-09-30 |
| 16 | `data/`, `models/`, `.kilo/`, `.opencode/`, `vendor/itto-src/` gitignored | GitHub 100 MB/file limit; provenance documented instead; unrelated worktrees excluded | 2026-09-30 |
| 17 | Global torch stays the CPU build (2.12.0+cpu) despite the RTX 3050 | Do not break other projects; code auto-detects CUDA/CPU | 2026-09-30 |

## Known Issues

- **D2 ML→EN returns junk** (OPEN; diagnosis started 2026-09-30): with the smoke-test load
  (`low_cpu_mem_usage=True`) the encoder outputs reaching `forward` during `generate()` are **all-NaN** →
  junk tokens ("to"). With `low_cpu_mem_usage=False` a direct forward gives the correct top-1
  "I" (p=0.4857). Raw weights measure clean in both load modes (0 NaN/Inf, max |w| ≤ 10). Root cause
  **NOT YET IDENTIFIED**; also open: the standalone D2 encoder call returns shape `(1,1,512)` instead of
  `(1,9,512)`. Measured details, next step, and diagnostic scripts: `docs/MODEL.md` § KNOWN ISSUE.
- `scripts/diagnose_ml_en.py` manual-loop path has a known argument bug (`input_ids=` instead of
  `decoder_input_ids=`) — superseded by `scripts/probe_ml_en_inputs.py`; not yet fixed.
- (No other implementation issues — `src/` not created yet.)

## Files

| File | Purpose | Status |
|---|---|---|
| `New Text Document.txt` | Authoritative project spec | exists |
| `AGENTS.md` | AI session instructions (wraps the spec) | exists |
| `README.md` | Onboarding: status, setup, next steps | exists (2026-09-30) |
| `requirements.txt` | Pinned, measured dependency versions | exists (2026-09-30) |
| `.gitignore` | Keeps >100 MB/local artifacts out of git | exists (2026-09-30) |
| `PRD.md` / `Architecture.md` / `Rules.md` / `Phases.md` / `Design.md` | Intent docs | exists (docs phase) |
| `docs/DATASET.md` | Dataset provenance, counts, license, planned splits | exists (2026-09-30) |
| `docs/MODEL.md` | Checkpoints, patches, smoke results, KNOWN ISSUE | exists (2026-09-30) |
| `docs/EVALUATION.md`, `docs/TOURISM_EVALUATION.md` | Evaluation reports | **not created** (only after real evaluation runs) |
| `Memory.md` | This file — persistent project state | exists |
| `scripts/patch_model_files.py` | transformers-v5 compat patches (idempotent) | exists (ran successfully) |
| `scripts/smoke_indicprocessor.py` | Preprocess/postprocess round-trip test | exists (**PASSED**) |
| `scripts/smoke_translate.py` | Real inference test (`enml` / `mlen`) | exists (`enml` **PASSED**; `mlen` reproduces the known issue) |
| `scripts/diagnose_ml_en.py`, `scripts/probe_ml_en_inputs.py`, `scripts/probe_ml_en_encoder.py`, `scripts/probe_ml_en_weights.py` | D2 diagnostics (4 scripts) | exist (all ran 2026-09-30; findings in `docs/MODEL.md`) |
| `vendor/IndicTransToolkit/`, `vendor/pyx_to_py.py` | Vendored preprocessing component + porting tool | exists (smoke-tested) |
| `vendor/itto-src/` | Upstream git clone (provenance) | exists locally, gitignored |
| `data/raw/samanantar/train-00000-of-00004.parquet` | Raw dataset shard (immutable) | exists (196,182,916 bytes), gitignored |
| `models/indictrans2-en-indic-dist-200M/`, `models/indictrans2-indic-en-dist-200M/` | Local patched checkpoints | exist, gitignored (patched `.py` files tracked) |
| `src/`, `tests/`, `notebooks/`, `data/processed/`, `data/tourism/` | Implementation (next phases) | **not created** |

## Commands

Verified executed successfully (2026-09-30, PowerShell, repo root):

```text
python scripts/patch_model_files.py                    # idempotent; prints "already applied" on rerun
python -u scripts/smoke_indicprocessor.py              # -> SMOKE 1 PASSED
python -u scripts/smoke_translate.py enml              # -> Malayalam outputs, SMOKE 2 enml PASSED
python -u scripts/smoke_translate.py mlen              # runs, but outputs junk "to" (known issue)
python -u scripts/diagnose_ml_en.py                    # ran (results in docs/MODEL.md)
python -u scripts/probe_ml_en_inputs.py                # ran
python -u scripts/probe_ml_en_encoder.py               # ran
python -u scripts/probe_ml_en_weights.py               # ran
```

Download commands are recorded in `docs/DATASET.md` / `docs/MODEL.md` (files byte-verified after download).
Console note: the smoke/probe scripts set UTF-8 themselves; for ad-hoc Python containing Malayalam use
`$env:PYTHONIOENCODING='utf-8'` first (Windows cp1252 crashes otherwise).

## Evaluation

All metrics are **NOT YET CALCULATED** — no formal evaluation has been run.
(Informal smoke timing, *not* an evaluation: D1 = 0.37 s/sentence, 2026-09-30, CPU, beam 5, 3-sentence smoke.)

| Metric | D1 En→Ml | D2 Ml→En | D3 Mg→En | D4 En→Mg |
|---|---|---|---|---|
| BLEU | NOT YET CALCULATED | NOT YET CALCULATED | NOT YET CALCULATED | NOT YET CALCULATED |
| chrF (if available) | NOT YET CALCULATED | NOT YET CALCULATED | NOT YET CALCULATED | NOT YET CALCULATED |
| Exact/acceptable match (curated phrases) | NOT YET CALCULATED | NOT YET CALCULATED | NOT YET CALCULATED | NOT YET CALCULATED |

| Component metric | Value |
|---|---|
| Category classification accuracy | NOT YET CALCULATED |
| NER precision / recall / F1 | NOT YET CALCULATED |
| WSD coverage / impact | NOT YET CALCULATED |
| Response time per direction | NOT YET CALCULATED |

When filled: each number requires its date, test set, and metric configuration (recorded with the number).

## Last Updated

- **2026-09-30 (2nd update)** — Onboarding docs created (`README.md`, `requirements.txt`, `.gitignore`,
  `docs/DATASET.md`, `docs/MODEL.md`, vendored-toolkit README); environment, dataset shard, and both
  checkpoints measured and recorded; D1 inference implemented and tested (0.37 s/sentence CPU); D2 known issue
  open with diagnosis started (4 diagnostic scripts run, findings recorded in `docs/MODEL.md`); this file
  rewritten to reflect measured state.
- **2026-09-30** — File created. Project documentation (`PRD.md`, `Architecture.md`, `Rules.md`, `Phases.md`,
  `Design.md`, `Memory.md`) written. No implementation, data, or measurements exist yet. Current phase:
  documentation complete, Phase 1 not started.
