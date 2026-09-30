# Malayalam Tourist Translation & Transliteration System

College NLP mini-project: a tourism-focused translation & transliteration app
for Kerala built around a **pretrained** multilingual model (IndicTrans2),
integrated with the course experiments 1–8 (string processing, preprocessing,
regex, n-grams, chunking/NER, HMM/Viterbi POS, WSD, word cloud/EDA).

Four directions:

| ID | Direction | How |
|---|---|---|
| D1 | English → Malayalam | IndicTrans2 EN→INDIC checkpoint |
| D2 | Malayalam → English | IndicTrans2 INDIC→EN checkpoint |
| D3 | Manglish → English | normalize Manglish (= Romanized Malayalam) → Malayalam → D2 |
| D4 | English → Manglish | D1 → Malayalam → Manglish transliteration |

> **Authoritative spec:** `New Text Document.txt` (read it first — it wins in any conflict).
> **Current state:** `Memory.md` · **AI-session instructions:** `AGENTS.md` · **Rules:** `Rules.md`

---

## Status at a glance (2026-09-30)

| Component | Status | Where |
|---|---|---|
| Documentation set (PRD/Architecture/Rules/Phases/Design/Memory) | ✅ done | repo root |
| Environment & dependencies | ✅ measured, pinned | `requirements.txt` |
| Dataset (Samanantar `ml` shard 0: 1,481,107 rows, CC-BY-NC-4.0) | ✅ downloaded & verified | `docs/DATASET.md` |
| Pretrained checkpoints (both directions, param counts verified, MIT) | ✅ downloaded & verified | `docs/MODEL.md` |
| IndicProcessor (IndicTransToolkit port — pip fails on Windows) | ✅ vendored, smoke-tested | `vendor/IndicTransToolkit/README.md` |
| transformers v5 compatibility patches | ✅ applied via script | `scripts/patch_model_files.py` |
| **D1 English → Malayalam** | ✅ **works end-to-end** (0.37 s/sentence, CPU, beam 5) | `scripts/smoke_translate.py enml` |
| **D2 Malayalam → English** | ⚠️ **OPEN KNOWN ISSUE** — returns "to"; weights measure clean, **all-NaN encoder output found in generate path**; diagnosis started (4 probe scripts ran), root cause not yet identified | `docs/MODEL.md` § KNOWN ISSUE |
| D3 / D4 Manglish directions | ⬜ planned (interfaces only so far) | `Phases.md` |
| `src/` modules (preprocessing, baselines, translation, evaluation) | ⬜ not started | — |
| Splits (`data/processed/`) & tourism set (`data/tourism/`) | ⬜ not started | `docs/DATASET.md` |
| Notebooks 01–04 | ⬜ not started | — |
| Evaluation (BLEU/chrF/…) | ⬜ **ALL METRICS NOT YET CALCULATED** | `docs/EVALUATION.md` *(to be created)* |
| UI (Streamlit) | ⬜ not started | `Design.md` |

---

## Setup on a fresh machine

```powershell
# 1) Python 3.13.5 (this project was built and measured on it)
pip install -r requirements.txt

# 2) Dataset — shard 0 only (see docs/DATASET.md for verification)
hf download AI4Bharat/Samanantar --repo-type dataset `
  --include "ml/train-00000-of-00004.parquet" --local-dir data/raw/samanantar
Move-Item data\raw\samanantar\ml\train-00000-of-00004.parquet data\raw\samanantar\

# 3) Checkpoints (exact commands: docs/MODEL.md)
#    D1: hf download naklitechie/indictrans2-en-indic-dist-200M --local-dir models/indictrans2-en-indic-dist-200M
#    D2: weights from Raghavan/... + tokenizer from hari31416/...-ONNX (details in docs/MODEL.md)

# 4) Patch checkpoint code for transformers v5 (ALWAYS after any re-download)
python scripts\patch_model_files.py

# 5) Smoke tests (expected final lines are printed by each script)
python -u scripts\smoke_indicprocessor.py      # -> SMOKE 1 PASSED
python -u scripts\smoke_translate.py enml      # -> Malayalam sentences + SMOKE 2 enml PASSED
```

The smoke scripts set `stdout` to UTF-8 themselves. **If you type Malayalam in a
plain `python -c` on Windows, set `$env:PYTHONIOENCODING='utf-8'` first** (the
console default cp1252 crashes on Malayalam).

---

## Repository layout

```
├── New Text Document.txt      # AUTHORITATIVE spec — read first
├── AGENTS.md                  # instructions for AI coding sessions
├── README.md                  # this file
├── Memory.md                  # persistent project state (source of truth for "what exists")
├── PRD.md / Architecture.md / Design.md / Phases.md / Rules.md
├── requirements.txt           # pinned, measured versions
├── docs/
│   ├── DATASET.md             # dataset provenance, counts, license, planned splits
│   └── MODEL.md               # checkpoints, patches, measured smoke results, KNOWN ISSUE
├── scripts/
│   ├── patch_model_files.py   # transformers-v5 compat patches (idempotent, re-runnable)
│   ├── smoke_indicprocessor.py# preprocess/postprocess round-trip test
│   ├── smoke_translate.py     # real inference test (enml | mlen)
│   ├── diagnose_ml_en.py      # D2: greedy vs beam vs manual-loop comparison (ran)
│   ├── probe_ml_en_inputs.py  # D2: dumps what generate feeds forward (ran)
│   ├── probe_ml_en_encoder.py # D2: NaN scan + D1/D2 encoder comparison (ran)
│   └── probe_ml_en_weights.py # D2: raw weight scan + load-mode comparison (ran)
├── vendor/
│   ├── IndicTransToolkit/     # vendored pure-Python port (+ README with provenance)
│   └── pyx_to_py.py           # the mechanical .pyx -> .py porting tool
├── data/                      # GITIGNORED — raw/processed/tourism (layout: docs/DATASET.md)
├── models/                    # GITIGNORED — local checkpoints (docs/MODEL.md)
├── src/                       # NOT YET CREATED — implementation goes here (Phase order: Phases.md)
└── notebooks/                 # NOT YET CREATED — 01..04 (Phases.md)
```

**Never push `data/` or `models/`** — GitHub rejects files > 100 MB (dataset
shard 187 MB, weights 1 GB / 871 MB). `.gitignore` already covers them;
provenance + re-download commands live in `docs/`.

---

## What to do next (ordered — for teammates & AI agents)

1. **Fix D2 (Malayalam → English)** — diagnosis already started; read
   `docs/MODEL.md` § KNOWN ISSUE first (measured findings + open questions).
   Next step **NOT YET RUN**: re-test with `low_cpu_mem_usage=False`
   (`scripts/smoke_translate.py mlen`), verify end-to-end, then explain the
   standalone encoder shape anomaly `(1,1,512)`. When `mlen` produces correct
   English, record the corrected outputs in `docs/MODEL.md`.
   *(D3 and the tourism evaluation wait for this.)*
2. **Create `src/`** in this order (per `Phases.md` dependencies):
   `config.py` (paths, device auto-detect, `sys.path` bootstrap for `vendor/`)
   → `preprocessing.py` (cleaning/validation, CSV/JSON export; never blind-lowercase Malayalam)
   → `translation.py` (`translate_en_to_ml` / `translate_ml_to_en`; validation, batching,
   error handling; **no hard-coded translations** — wrap the recipe in `scripts/smoke_translate.py`).
3. **Sample & split the dataset** reproducibly (80/10/10, seed 42, dedup across
   splits) → `data/processed/{train,validation,test}.csv`; fill the measured
   numbers into `docs/DATASET.md`; notebook `notebooks/01_dataset_analysis.ipynb`.
4. **Tourism set** → `data/tourism/` (8 categories, real parallel pairs only,
   never fabricated; fields `english, malayalam, category`; same seeded split).
5. **Baselines:** `src/ngram_baseline.py` (bigram+trigram next-word on the real
   corpus) and `src/translation_baseline.py` (exact/phrase lookup) — needed as
   the comparison point for the evaluation.
6. **Evaluation** → `src/evaluation.py` + `notebooks/04_translation_evaluation.ipynb`
   → `docs/EVALUATION.md` (BLEU/chrF both directions, baseline vs transformer,
   timing) and `docs/TOURISM_EVALUATION.md` + error analysis from **real outputs only**.
   Every number: measured, dated, with its configuration. Anything uncomputed
   stays **NOT YET CALCULATED**.
7. **Finish:** notebooks 02/03, UI (`Design.md`), Part 19 validation checklist
   (`Phases.md`), then git status/diff/log before & after committing (Part 20).

---

## Non-negotiable rules (full text: `Rules.md`, `AGENTS.md`)

- **No fabricated data** — no invented counts, BLEU scores, translations, or
  capability claims. Future items are marked *planned*; unmeasured numbers are
  *NOT YET CALCULATED*; uncertainties are *DECISION REQUIRED* / *ASSUMPTION*.
- The translation model is **pretrained** — never claim the team trained it;
  fine-tuning has **not** been performed.
- `data/raw/` is immutable; keep `raw/` · `processed/` · `tourism/` separate.
- Every documented command must have actually been run successfully.
- Git safety (Part 20): no `reset`, no branch deletion, no remote changes;
  capture `git status` / `diff` / `log` before **and** after.

## Environment notes / troubleshooting

- **torch is CPU-only** (`2.12.0`) even though an RTX 3050 exists — do not
  upgrade the global torch (would break other projects). Code auto-detects
  CUDA/CPU and runs fp32 on CPU.
- **`pip install indictranstoolkit` fails on Windows** (no wheels/MSVC) → use
  `vendor/IndicTransToolkit/` (port provenance in its README).
- **transformers 5.12.1 vs 4.x-era checkpoint code** → run
  `scripts/patch_model_files.py` after every model download; if you re-download,
  patches must be re-applied (the script is idempotent).
- **`IndicProcessor` blocks forever** → you called `preprocess_batch` /
  `postprocess_batch` unpaired; they must be matched per instance (see
  `vendor/IndicTransToolkit/README.md`).
- Official AI4Bharat checkpoints are **gated (401)** — this machine has no HF
  token, hence the ungated mirrors recorded in `docs/MODEL.md`.
