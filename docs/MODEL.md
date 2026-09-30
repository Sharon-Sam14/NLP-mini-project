# MODEL — IndicTrans2 (pretrained, inference only)

**The team did NOT train this model.** IndicTrans2 is used as a *pretrained*
seq2seq model via official inference code. **No fine-tuning has been performed**
(hence there is intentionally no `src/train.py`; if fine-tuning is ever done, it
must be added and documented separately).

**Status (2026-09-30):** EN→ML **works end-to-end** (measured below).
ML→EN has an **OPEN KNOWN ISSUE** in `generate()` (weights verified good).

## Checkpoints

| Direction | Official repo (gated ⚠) | Local source used | Params (counted) | License | Lang codes |
|---|---|---|---|---|---|
| D1 EN → ML | `ai4bharat/indictrans2-en-indic-dist-200M` — returns **HTTP 401** without an HF token (this machine has none) | mirror `naklitechie/indictrans2-en-indic-dist-200M` (param count matches official exactly) | 274,584,576 | MIT | `eng_Latn` → `mal_Mlym` |
| D2 ML → EN | `ai4bharat/indictrans2-indic-en-dist-200M` — same gating | weights `Raghavan/indictrans2-indic-en-dist-200M` (`pytorch_model.bin`, 228,316,160 params = official count) + tokenizer/config/custom code from `hari31416/indictrans2-indic-en-dist-200M-ONNX` (mirror of the official repo) | 228,316,160 | MIT | `mal_Mlym` → `eng_Latn` |

Lang codes are FLORES-200 codes and are prepended by `IndicProcessor` as
`"{src} {tgt} "` tags; Malayalam input is transliterated to Devanagari for the
model and back afterwards. **This is the model's own convention — not something we invented.**

## Re-download (reproducible)

```powershell
# D1 (everything from one mirror)
hf download naklitechie/indictrans2-en-indic-dist-200M --local-dir models/indictrans2-en-indic-dist-200M

# D2 weights
hf download Raghavan/indictrans2-indic-en-dist-200M --local-dir models/indictrans2-indic-en-dist-200M
# D2 tokenizer + config + custom code (ONNX mirror of the official repo — take everything except *.onnx)
hf download hari31416/indictrans2-indic-en-dist-200M-ONNX --local-dir models/tmp-mlen-onnx
Get-ChildItem models\tmp-mlen-onnx -File | Where-Object { $_.Extension -ne '.onnx' } |
  Copy-Item -Destination models\indictrans2-indic-en-dist-200M\
Remove-Item models\tmp-mlen-onnx -Recurse

# ALWAYS patch after (re)downloading — see next section
python scripts\patch_model_files.py
```

`models/` is **gitignored** (weights are 1 GB / 871 MB — GitHub rejects > 100 MB files).

## transformers v5 compatibility patches (required)

The checkpoint code was written for transformers **4.x**; this machine runs
**5.12.1**. `scripts/patch_model_files.py` applies mechanical,
**inference-neutral** patches to both local model copies (idempotent — re-run
after every re-download):

| # | File | v5 break | Patch |
|---|---|---|---|
| 1 | `configuration_indictrans.py` | `transformers.onnx` module removed | import wrapped in try/except with a stub (ONNX export never used) |
| 2 | `tokenization_indictrans.py` | special tokens may not be assigned before `super().__init__()` | `__init__` reordered (unwrap tokens → load/validate vocabs → `super()` → switch mode → cache ids) |
| 3 | `modeling_indictrans.py` (both) | `tie_weights()` now called with kwargs; `_tie_or_clone_weights` removed | accepts `*args/**kwargs`; ties by sharing the Parameter directly (same direction as v4) |
| 4 | `modeling_indictrans.py` (ML→EN copy) | v5 no longer inherits `GenerationMixin` from `PreTrainedModel` | explicit inheritance added |
| 5 | `configuration_indictrans.py` (ML→EN copy) | `config.json` lacks `vocab_size` → beam search crashes | derived from `decoder_vocab_size` |
| 6 | `modeling_indictrans.py` (ML→EN copy) | forward called a teacher-forcing helper that trims the last decoder token and requires a non-None mask | upstream generation contract restored |
| 7 | `modeling_indictrans.py` (both) | v5 generation passes/returns `Cache` objects; model consumes/produces legacy tuples | Cache⇄tuple bridge: forward entry/exit, `_reorder_cache`, two helper methods |

No model logic, weights, or tokenization behaviour is changed. Patches are
tracked in git (`scripts/patch_model_files.py`); the model dirs themselves are
mostly gitignored.

## Preprocessing component (vendored)

`IndicProcessor` comes from AI4Bharat's **IndicTransToolkit** (MIT), which
**cannot be pip-installed on Windows** (Cython ext needs MSVC). A pure-Python
port lives at `vendor/IndicTransToolkit/` — provenance & reproduction:
`vendor/IndicTransToolkit/README.md`.

Upstream contract: `preprocess_batch()` and `postprocess_batch()` must be
called as **matched pairs** per instance (postprocess clears a leftover queue;
unpaired calls block forever).

## Inference recipe (as run)

`IndicProcessor.preprocess_batch` → `AutoTokenizer(..., trust_remote_code=True)`
→ `model.generate(max_length=256, num_beams=5)` → `batch_decode(skip_special_tokens=True,
clean_up_tokenization_spaces=True)` → `IndicProcessor.postprocess_batch(lang=tgt)`.
Device auto-detected (`torch.cuda.is_available()`); on this machine it is
**CPU, fp32** (global torch is a CPU build — do not upgrade it; the RTX 3050 is
unused). Whole recipe implemented in `scripts/smoke_translate.py` and later in `src/translation.py`.

## Measured smoke results (2026-09-30, CPU, beam 5)

Command: `python -u scripts/smoke_translate.py enml`

| EN input | ML output (raw model output) |
|---|---|
| I need a taxi. | എനിക്ക് ഒരു ടാക്സി വേണം. |
| Where is the nearest hotel? | ഏറ്റവുംഅടുത്തുള്ള ഹോട്ടൽ എവിടെയാണ്? |
| How much does this cost? | ഇതിന് എത്ര ചെലവാകും? |

Timing: **3 sentences in 1.1 s → 0.37 s/sentence** (measured; BLEU etc. remain
**NOT YET CALCULATED** — evaluation phase not run).

## ⚠ KNOWN ISSUE — ML→EN returns junk (OPEN; diagnosis started)

**Symptom (measured):** `python -u scripts/smoke_translate.py mlen` prints
`EN: to` for every input (1 token then stop).

**Measured healthy (2026-09-30):**

- Raw `pytorch_model.bin`: 913,515,337 bytes, 767 keys — **0 tensors with
  NaN/Inf, max |weight| ≤ 10** (same for both load modes).
- Loaded model: 228,316,160 params = official count; tensor names identical to
  the working D1 model; source tokenization has **0 `<unk>`**; dict sizes match
  config (SRC 122706 / TGT 32296).
- With `low_cpu_mem_usage=False`: a direct forward pass predicts the correct
  first token **"I" (p=0.4857)** (then A 0.0495, taxi 0.0075).

**Measured failure state (with the current smoke-test load,
`low_cpu_mem_usage=True`):**

- The encoder outputs reaching `forward` during `generate()` are **all-NaN** →
  logits all-NaN → argmax returns junk ("to"). Greedy → ids `[2,0,0,0,...]`;
  beam-5 → `[2,8]` ("to") (`scripts/diagnose_ml_en.py`).
- The same internal forward with `low_cpu_mem_usage=False` produced normal
  activations and finite, correct logits — the result depends on the load mode
  even though weights measure clean in both modes. **Root cause NOT YET IDENTIFIED.**

**Open anomaly:** the standalone D2 encoder call returns shape `(1,1,512)`
(all-NaN under `low_cpu_mem_usage=True`) instead of `(1,9,512)`; the D1 control
returns its full sequence `(1,8,512)`. Cause not yet identified.

**Diagnostic scripts (all created and run 2026-09-30):** `diagnose_ml_en.py`
(greedy/beam/manual comparison; its manual-loop path has a known argument bug —
passes `input_ids=` instead of `decoder_input_ids=` — superseded by the probe
below), `probe_ml_en_inputs.py` (dumps what generate feeds forward),
`probe_ml_en_encoder.py` (NaN scan + encoder/forward comparison D1 vs D2),
`probe_ml_en_weights.py` (raw weight-magnitude scan + load-mode comparison).

**Next step (NOT YET RUN):** load with `low_cpu_mem_usage=False` in the smoke
test, re-run `scripts/smoke_translate.py mlen`, verify end-to-end; then explain
the standalone encoder shape anomaly. Record the outcome here.

## Planned (not started)

- `src/translation.py` exposing `translate_en_to_ml` / `translate_ml_to_en`
  (validation, batching, error handling, no hard-coded translations).
- Optional fine-tuning: **not performed** (documented as not performed unless it actually happens).
- Evaluation (BLEU/chrF/timing, both directions, baseline vs transformer) → `docs/EVALUATION.md`.
