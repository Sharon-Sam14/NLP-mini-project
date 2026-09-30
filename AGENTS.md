# AGENTS.md — Malayalam Tourist Translation & Transliteration System

## Authoritative specification

The complete project spec lives in **`New Text Document.txt`** (repo root). Read that file first in every new session before doing any work. It is the single source of truth for scope, deliverables, phase order, and rules. This AGENTS.md only summarizes it; if anything here conflicts with the spec file, the spec file wins.

## What this project is

College NLP mini-project: a tourism-focused translation & transliteration system with four directions:

1. English → Malayalam
2. Malayalam → English
3. Manglish → English (Manglish = Malayalam written in Roman characters, never an independent language)
4. English → Manglish (via English → Malayalam → Malayalam → Manglish)

## Current phase (updated 2026-09-30)

Documentation phase is **complete**: `PRD.md`, `Architecture.md`, `Rules.md`, `Phases.md`, `Design.md`, and `Memory.md` all exist. Onboarding entry point for humans **and agents** = `README.md` (status table + ordered next steps).

Setup state (all measured, 2026-09-30): `requirements.txt` pinned to the verified environment; Samanantar `ml` shard 0 downloaded and verified (`docs/DATASET.md`); both IndicTrans2 checkpoints downloaded and verified (`docs/MODEL.md`); IndicTransToolkit vendored as a pure-Python port (pip install fails on Windows); `scripts/patch_model_files.py` provides the transformers-v5 compatibility patches; smoke tests run from `scripts/`. **D1 (EN→ML) inference works end-to-end (tested). D2 (ML→EN) has an open KNOWN ISSUE — diagnosis started, findings recorded in `docs/MODEL.md`.**

Not created yet: `src/`, dataset splits, tourism set, baselines, evaluation, notebooks, UI. Next work = the README next-steps list (item 1: D2 known issue), then create `src/` in `Phases.md` dependency order — do not start any phase before its `Phases.md` dependencies are validated.

Session rules:

- Read `Memory.md` for current state (it is the source of truth for what exists/measured); update it after every major completed phase.
- Keep all six docs internally consistent when making decisions; follow `Rules.md` (especially §14 AI coding rules and the no-fabrication rules).

## Hard rules (from the spec)

- **No fabricated data**: no invented dataset sizes, BLEU scores, accuracy, translations, API availability, or completed features. Future items must be clearly marked as planned; unresolved items as `DECISION REQUIRED` / `ASSUMPTION`.
- Documentation must explicitly connect the project to course **Experiments 1–8** (string processing, preprocessing, regex, n-grams, chunking/NER, HMM/Viterbi/POS, WSD, word cloud/EDA).
- Translation model: a pretrained multilingual model (e.g., IndicTrans2) may be used; never claim the team trained it from scratch.
- Datasets (e.g., AI4Bharat Samanantar/BPCC) must be documented with name, source, license, sentence-pair counts (measured, not guessed), preprocessing, and split.
- Evaluation must be measurable (BLEU/chrF/exact match/NER F1/response time) with actual measured values in the final report.
- Recommended stack only: Python, Pandas, NLTK, spaCy where appropriate, Hugging Face Transformers, PyTorch, Streamlit, Matplotlib, SacreBLEU/NLTK BLEU. No unnecessary technologies.

## Working style

- Inspect existing files before editing; one logical change at a time.
- Documentation must be internally consistent and practical enough that another AI assistant can implement the project phase by phase without guessing requirements.

## Tooling notes (this workspace)

- **graphify**: the project-local plugin lives at `.opencode/plugins/graphify.js` (auto-loaded by OpenCode from `.opencode/plugins/`, no config reference needed); the global graphify skill (`~/.config/opencode/skills/graphify/`) and the `graphify` CLI apply here too. The plugin's shell-command reminder only activates once `graphify-out/graph.json` exists (after a `/graphify` run). `.opencode/` stays untracked — don't commit it unless asked.
