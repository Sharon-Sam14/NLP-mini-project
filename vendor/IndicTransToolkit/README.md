# IndicTransToolkit — vendored pure-Python port

Local, **vendored** copy of AI4Bharat's
[`IndicTransToolkit`](https://github.com/AI4Bharat/IndicTransToolkit) (MIT —
see `LICENSE`), providing `IndicProcessor`, the preprocessing/postprocessing
component required by IndicTrans2 (language-tagging, script transliteration to
Devanagari, detokenization, placeholder protection).

## Why vendored instead of pip-installed

`pip install indictranstoolkit` **fails on this Windows machine**: the package
ships a Cython extension (`processor.pyx`) with no prebuilt Windows wheels, and
MSVC Build Tools are not installed. WSL was rejected to keep one environment.
So `processor.pyx` was ported to pure Python mechanically (see below).

## What's here

| File | Provenance |
|---|---|
| `processor.py` | **Ported** from upstream `IndicTransToolkit/processor.pyx` **v1.1.1**, commit `3efb8418d0721b4ce267c2b3586899d313191357`, with `../pyx_to_py.py` (mechanical transformation — no logic lines altered) |
| `evaluator.py` | **Copied unmodified** from upstream (self-contained; uses sacrebleu + indicnlp) |
| `__init__.py` | exports `IndicProcessor`, `IndicEvaluator` |
| `LICENSE` | upstream MIT license |

Upstream's full git clone lives at `../itto-src/` for provenance (gitignored —
it is someone else's repo; keep it local).

## Reproduce the port

```powershell
git clone https://github.com/AI4Bharat/IndicTransToolkit vendor/itto-src
git -C vendor/itto-src checkout 3efb8418d0721b4ce267c2b3586899d313191357   # pinned version actually ported
python vendor/pyx_to_py.py vendor/itto-src/IndicTransToolkit/processor.pyx vendor/IndicTransToolkit/processor.py
```

## Usage + the pairing contract

```python
import sys; sys.path.insert(0, "vendor")
from IndicTransToolkit import IndicProcessor

ip = IndicProcessor(inference=True)
pre = ip.preprocess_batch(["I need a taxi."], src_lang="eng_Latn", tgt_lang="mal_Mlym")
# ... model.generate(...) ...
post = ip.postprocess_batch(model_outputs, lang="mal_Mlym")
```

⚠ **Upstream contract:** `preprocess_batch()` and `postprocess_batch()` must be
called as *matched pairs* (same number of sentences) on the same instance —
`postprocess_batch()` pops the placeholder maps and then **clears the queue**;
unpaired calls make the next call block forever.

## Test

```powershell
python -u scripts/smoke_indicprocessor.py     # expected final line: SMOKE 1 PASSED
```

(Verified passing 2026-09-30: EN/ML preprocessing tags, Devanagari↔Malayalam
script conversion, Moses-style English detokenization.)
