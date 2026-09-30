# PRD — Malayalam Tourist Translation & Transliteration System

| | |
|---|---|
| **Project** | Malayalam Tourist Translation & Transliteration System |
| **Type** | College NLP mini-project |
| **Status** | Documentation phase — no implementation yet (all requirements below are **planned** unless explicitly marked otherwise) |
| **Created** | 2026-09-30 |

> Marker convention used throughout this documentation (also mandated in `Rules.md`):
> **NOT YET CALCULATED** = value exists but has not been computed · **DECISION REQUIRED** = unresolved choice ·
> **ASSUMPTION** = unverified guess · **planned** = specified but not implemented.

---

## 1. Project overview

A lightweight, FOSS-only NLP application that helps tourists in Kerala communicate in four translation directions:

1. English → Malayalam
2. Malayalam → English
3. Manglish → English
4. English → Manglish

**Manglish** means Malayalam written using English/Roman characters. It is treated throughout this project as
*Romanized Malayalam* — never as an independent natural language.

The system combines a **pretrained multilingual translation model** (candidate: the IndicTrans2 model family) with
course NLP components — string processing, preprocessing, regular expressions, n-grams, chunking/NER, HMM/Viterbi POS,
WSD, and corpus EDA — to produce a tourism-focused communication tool with measurable evaluation.

The application is scoped to **tourist communication in Kerala** and delivered as a simple desktop-run web UI
(Streamlit), consistent with an academic mini-project.

## 2. Problem statement

Tourists in Kerala regularly need to ask for taxis, check in to hotels, order food, find directions, shop, and — most
critically — handle emergencies, in a language they may not speak. General-purpose translation tools exist, but:

- They are not **anchored to tourism contexts** (categories, entities such as hotels, stations, prices, phone numbers).
- **Manglish** — the everyday Romanized Malayalam used in messages, driver chats, signage transliterations and search
  queries — has no systematic support as either a *source* or a *target* form in a single focused tool.
- There is no lightweight, offline-capable, academically transparent artifact that shows *how* NLP preprocessing,
  entity extraction, disambiguation and evaluation contribute to a translation workflow.

## 3. Motivation

- **Practical:** Tourism is central to Kerala's economy; language barriers directly affect trip quality and safety.
- **Linguistic:** Manglish is widely used but underserved; treating it as Romanized Malayalam (with an explicit
  transliteration/normalization path) is both correct and useful.
- **Academic:** The project integrates all eight course NLP experiments (Section 9) into one coherent, measurable
  system instead of eight isolated lab exercises.

## 4. Target users

| User | Need |
|---|---|
| Domestic & international tourists | Produce usable Malayalam/Manglish sentences from English; understand Malayalam/Manglish replies |
| Local service providers (drivers, hotel staff, shopkeepers) | Understand Manglish/English queries; reply in Malayalam |
| Students & evaluators (course context) | A demonstrable, testable NLP system with honest metrics |
| Presentation/demo audience | Simple UI showing translation + detected category + entities live |

## 5. Goals

| ID | Goal | How it is verified |
|---|---|---|
| G1 | Working translation in all four directions | End-to-end run through the UI (Phase 12) |
| G2 | Tourism-aware output: category detection + entity extraction | Category accuracy and NER P/R/F1 measured on labeled data (Phase 13) |
| G3 | Honest, reproducible evaluation | BLEU/chrF/exact-match recorded in `Memory.md` from actual runs only |
| G4 | An n-gram language-model baseline for comparison | Baseline built from corpus counts; compared against the main pipeline (Phase 7/13) |
| G5 | Corpus understanding via EDA and word clouds | EDA report artifacts generated from the real corpus (Phase 6) |
| G6 | Simple, accessible UI | Streamlit app per `Design.md`, mobile-responsive, Unicode-correct (Phase 14) |

Numeric targets (e.g., minimum BLEU): **DECISION REQUIRED** — to be set in Phase 13 before evaluation runs, never
chosen after seeing results.

## 6. Supported translation directions

Manglish definition and the canonical reference triplet (spec-provided examples — these are *reference expectations*,
not measured model outputs, and are candidates for the curated test phrases):

| Language | Example |
|---|---|
| English | "I need a taxi." |
| Malayalam | "എനിക്ക് ഒരു ടാക്സി വേണം." |
| Manglish | "Enikku oru taxi venam." |

### 6.1 Direction table (as implemented)

| # | Direction | Internal route | Example (reference) |
|---|---|---|---|
| D1 | English → Malayalam | preprocess → translation model → post-process | "I need a taxi." → "എനിക്ക് ഒരു ടാക്സി വേണം." |
| D2 | Malayalam → English | preprocess → translation model → post-process | "എനിക്ക് ഒരു ടാക്സി വേണം." → "I need a taxi." |
| D3 | Manglish → English | Manglish→Malayalam normalization/transliteration → Malayalam→English translation → English | "Enikku oru taxi venam." → "I need a taxi." |
| D4 | English → Manglish | English→Malayalam translation → Malayalam→Manglish transliteration → Manglish | "I need a taxi." → "Enikku oru taxi venam." |

An internal **Malayalam → Manglish** transliteration capability is required as a building block for D4 (and a
Malayalam → Manglish step may be offered as an auxiliary capability), but the four directions above are the product
scope.

## 7. Tourism categories

The system detects and/or lets the user select one of eight categories:

| # | Category | Example phrase (English) |
|---|---|---|
| C1 | Hotel / Accommodation | "I have a booking under the name Sharma." |
| C2 | Food / Restaurant | "Is this dish spicy?" |
| C3 | Transportation | "I need a taxi to the airport." |
| C4 | Directions | "Where is the nearest ferry jetty?" |
| C5 | Shopping | "What is the price of this saree?" |
| C6 | Sightseeing | "When does the boat tour start?" |
| C7 | Emergency | "Call a doctor, please!" |
| C8 | General Conversation | "Thank you very much." |

Category detection is **planned** to be rule/keyword-based first (with measured accuracy), with statistical
classification as a possible later option — see `Phases.md` Phase 8/13.

## 8. Functional requirements

All requirements are **planned** (nothing implemented at documentation time).

| ID | Requirement | Notes |
|---|---|---|
| FR-1 | Translate English → Malayalam with the selected pretrained model | D1 |
| FR-2 | Translate Malayalam → English | D2 |
| FR-3 | Translate Manglish → English via Malayalam normalization + D2 | D3 |
| FR-4 | Translate English → Manglish via D1 + Malayalam→Manglish transliteration | D4 |
| FR-5 | Detect the tourism category of the input (and allow manual override) | Accuracy measured later |
| FR-6 | Extract and display entities: locations, hotels, restaurants, people, organizations, dates, money, phone numbers, prices, URLs | Rule/regex + chunking based |
| FR-7 | Display source text, output text, category and entities together | Per `Design.md` |
| FR-8 | Switch among the four directions in one click | UI requirement |
| FR-9 | Graceful error states: empty input, wrong script for direction, model unavailable — never fabricate an output | See Rules §4/§13 |
| FR-10 | Generate EDA artifacts (word frequency, word clouds, category distribution, vocabulary stats) from the real corpus | Files, not necessarily UI |
| FR-11 | Generate an evaluation report (BLEU/chrF/exact match/NER F1/response time) from frozen test sets | Numbers → `Memory.md` |
| FR-12 | Provide an n-gram next-word prediction baseline over the tourism corpus | Course Experiment 4 |
| FR-13 | Persist no user data; run locally without paid APIs | FOSS constraint |

## 9. NLP requirements — mapping course experiments to the system

| Experiment | Course concept | System requirement | Used in |
|---|---|---|---|
| E1 String Processing | Unicode handling, split/join, replacement, word counting, case handling, Malayalam Unicode preservation | Unicode-safe text operations module; Malayalam strings must survive round-trips byte-identically; case folding only for English/Manglish matching | All pipelines |
| E2 Text Preprocessing | Tokenization, normalization, filtering, punctuation/whitespace handling, Malayalam-aware preprocessing | Shared cleaner/tokenizer used consistently for corpus, baselines and translation inputs | Preprocessing pipeline, N-gram, NER, EDA |
| E3 Regular Expressions | Numbers, prices, currency, phone numbers, URLs, special patterns | Pattern library for tourism entities (money, phone, URL, prices) feeding FR-6 | NER pipeline |
| E4 N-gram Model | Bigram/trigram, next-word prediction, LM baseline | Corpus-derived n-gram model; next-word suggestion baseline; comparison reference for translation quality discussion | Baseline + evaluation context |
| E5 Chunking & NER | Noun phrases; locations, hotels, restaurants, people, organizations, dates, money | Chunker + entity extractor with measured precision/recall/F1 | NER pipeline (FR-6) |
| E6 HMM / Viterbi / POS | Sequence model / POS tagging | Optional component — used **only where it demonstrably helps** (e.g., tagging for chunking or disambiguation); explicitly **not forced** into the translation path | Optional; documented honestly if unused |
| E7 Word Sense Disambiguation | Lesk-style WSD; ambiguity in context; how WSD supports translation | Lesk-style WSD over tourism-relevant ambiguous words; demonstrate ambiguity with context; document where sense choice affects translation output | WSD pipeline |
| E8 Word Cloud & EDA | Word frequency, word clouds, category distribution, vocabulary analysis, further EDA suggestions | EDA report over the tourism corpus + suggested additional analyses | EDA pipeline (FR-10) |

## 10. Dataset requirements

Four dataset classes are required:

1. **General English–Malayalam parallel corpus** (background/domain-robustness)
2. **Tourism-specific English–Malayalam dataset** (target domain)
3. **Manglish–Malayalam paired dataset** (for transliteration/normalization)
4. **Test datasets for all four directions** (frozen before evaluation)

Planned layout (spec-mandated):

```
data/
├── raw/          # untouched downloads, per-dataset subfolders
├── processed/    # cleaned/normalized outputs
├── tourism/      # tourism-domain parallel data
└── test/         # frozen test sets per direction (D1–D4)
```

**Recording requirements (mandatory for every dataset):** dataset name · source · license · number of sentence pairs ·
preprocessing performed · train/validation/test split.

Candidate sources to evaluate at collection time: AI4Bharat resources such as **Samanantar** and **BPCC**, and any
tourism-domain parallel data the team can legally collect. Candidate ≠ collected: sizes, licenses and pair counts are
recorded **only after actual download and verification** — never estimated. No fabricated dataset sizes anywhere in
this documentation.

## 11. Translation requirements

- Use a **pretrained multilingual translation model**; training a large translation model from scratch is out of
  scope. The IndicTrans2 model family is the **candidate** because it supports English and Malayalam.
- **The team does not claim to have trained IndicTrans2.** It is used as a pretrained model; the exact checkpoint,
  version/source URL, language tags and license are recorded in `Memory.md` **when actually downloaded** (Phase 10).
- If fine-tuning is performed later, it is documented **separately** from pretrained usage.
- Input must pass through the shared preprocessing pipeline; output through post-processing (whitespace/punctuation
  restoration, script checks).
- Manglish routes (D3/D4) must round-trip through Malayalam — Manglish is never translated "directly" as its own
  language.
- If the model is unavailable (not downloaded, runtime error), the UI must show an **error state** — it must never
  fabricate a translation (Rules §4).

## 12. Evaluation requirements

The project must be measurable. Evaluate at minimum:

| Direction | Required metrics |
|---|---|
| D1 English → Malayalam | BLEU; chrF if available; response time |
| D2 Malayalam → English | BLEU; chrF if available; response time |
| D3 Manglish → English | BLEU; exact/acceptable match on curated tourist phrases; response time |
| D4 English → Manglish | BLEU; exact/acceptable match on curated tourist phrases; response time |

Additional measured metrics:

- **Category classification accuracy** (FR-5)
- **NER precision / recall / F1** (FR-6) on a hand-labeled sample
- **Response time** per direction (mean over repeated runs, hardware noted)

Rules:

- Evaluation runs only against **frozen test sets** (created in Phase 2/13, never modified after first run).
- Metric configuration (tokenizer, smoothing, casing) is recorded alongside results for reproducibility.
- **No invented evaluation results anywhere.** The final report and `Memory.md` contain only actually measured
  values; everything else stays **NOT YET CALCULATED**.

## 13. User workflow

```
Start app (Streamlit)
   → Choose translation direction  [ English → Malayalam ▼ ]
   → Type or paste a sentence        [ Enter your sentence ]
   → (Optional) category auto-detected / manually overridden
   → Click [ Translate ]
   → Read: output text + detected category + detected entities
   → Switch direction as needed (one click) and continue
```

Failure paths: empty input → inline hint; script/direction mismatch → warning before running; model unavailable →
error state (no fabricated output).

## 14. Non-functional requirements

| ID | Requirement |
|---|---|
| NFR-1 | **FOSS only** — no paid APIs, no cloud dependencies, no proprietary SDKs |
| NFR-2 | **Offline operation** after model/dataset download |
| NFR-3 | **Unicode correctness** — UTF-8 end-to-end; Malayalam survives storage, processing and display unaltered |
| NFR-4 | **Performance** — response time measured and recorded; acceptable threshold **DECISION REQUIRED** (set in Phase 13 before measuring) |
| NFR-5 | **Reproducibility** — fixed random seeds; dataset splits and test sets frozen; commands documented in `Memory.md` |
| NFR-6 | **Accessibility** — labelled controls, keyboard operation, adequate contrast (per `Design.md`) |
| NFR-7 | **Responsiveness** — usable on phone-sized screens |
| NFR-8 | **Data hygiene** — no user input persisted; no external transmission |

## 15. Non-goals

- Not a general-purpose MT engine competing with commercial systems.
- **No training of a translation model from scratch.**
- No speech recognition/speech synthesis, no OCR, no camera/AR features.
- No messaging-app integrations (WhatsApp/Telegram bots) in this project.
- No proprietary/paid APIs or cloud services.
- Manglish is **not** treated as an independent natural language.
- Not an authoritative translation service for legal/medical contexts (academic demonstration).
- No production-grade SLA, multi-user backend, or accounts/auth.

## 16. Success criteria

Each criterion is verified by a concrete test; numeric thresholds are decided in Phase 13 **before** evaluation, and
every reported number is measured:

| ID | Criterion | Verification |
|---|---|---|
| SC-1 | All four directions run end-to-end in the UI | Manual test script over the reference examples (Phase 12) |
| SC-2 | BLEU (+ chrF where available) measured and recorded for D1–D4 | Evaluation report → `Memory.md` (Phase 13) |
| SC-3 | Curated tourist-phrase exact/acceptable match measured for D3/D4 | Held-out curated list, scored automatically |
| SC-4 | Category accuracy measured on labeled samples | Confusion matrix + accuracy recorded |
| SC-5 | NER precision/recall/F1 measured against hand-labeled data | Scores recorded |
| SC-6 | Response time measured per direction and recorded | Timed runs, hardware noted |
| SC-7 | EDA/word-cloud artifacts generated from the real corpus | `reports/` outputs exist and are reproducible |
| SC-8 | n-gram baseline operational and compared in the report | Next-word predictions sample + comparison table |
| SC-9 | Documentation consistent; `Memory.md` current after each phase | Docs review checklist (Rules §16) |
| SC-10 | Test suite passes from a clean checkout following documented commands | `python -m unittest` (Rules §15) |

Minimum numeric thresholds for SC-2..SC-6: **DECISION REQUIRED** (Phase 13, pre-registered before runs).

## 17. Future scope

- Fine-tuning the pretrained model on the collected tourism corpus (documented separately if attempted)
- Additional languages (Tamil, Hindi, German, …)
- Speech input/output; OCR of signage
- On-device/mobile packaging
- Browser extension for translating chat messages
- Larger curated tourism glossary and phrasebook
- Expanded WSD coverage and POS-driven disambiguation at scale (only if E6 proves useful in Phase 9)
- Integration of user feedback loops for phrase correction

---

*This document specifies requirements only. No application code is built during the documentation phase
(see `Phases.md`). Implementation begins at Phase 1.*
