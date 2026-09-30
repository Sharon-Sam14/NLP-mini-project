"""Smoke test 2: pretrained IndicTrans2 inference on the local checkpoints.

Usage:
    python -u scripts/smoke_translate.py enml   # English  -> Malayalam (D1)
    python -u scripts/smoke_translate.py mlen   # Malayalam -> English  (D2)

Prerequisites:
    - checkpoints present in models/            (download: docs/MODEL.md)
    - python scripts/patch_model_files.py run once after every download

Prints RAW model output (no pre-baked translations anywhere).

Measured 2026-09-30, CPU (torch 2.12.0+cpu, transformers 5.12.1, beam 5):
    enml: 3 sentences in 1.1 s  (0.37 s/sentence) — outputs in docs/MODEL.md
    mlen: currently reproduces the KNOWN ISSUE (docs/MODEL.md);
          use scripts/diagnose_ml_en.py to investigate.
"""
import os
import sys
import time
from pathlib import Path

os.chdir(Path(__file__).resolve().parents[1])  # repo root
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # Windows console is cp1252
sys.path.insert(0, "vendor")

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from IndicTransToolkit import IndicProcessor

EN_ML = "models/indictrans2-en-indic-dist-200M"
ML_EN = "models/indictrans2-indic-en-dist-200M"

device = "cuda" if torch.cuda.is_available() else "cpu"
print("device:", device, "| torch:", torch.__version__, flush=True)

ip = IndicProcessor(inference=True)


def load(model_dir):
    t0 = time.time()
    tok = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)
    print(f"tokenizer loaded ({type(tok).__name__}) in {time.time()-t0:.1f}s", flush=True)
    t0 = time.time()
    model = AutoModelForSeq2SeqLM.from_pretrained(
        model_dir, trust_remote_code=True, low_cpu_mem_usage=True
    )
    model.to(device).eval()
    print(f"model loaded in {time.time()-t0:.1f}s on {device}", flush=True)
    return tok, model


def translate_batch(model, tok, texts, src, tgt):
    """Official IndicTrans2 recipe: preprocess -> tokenize -> generate -> decode -> postprocess."""
    pre = ip.preprocess_batch(texts, src, tgt)
    enc = tok(pre, return_tensors="pt", padding=True, truncation=True, max_length=256)
    enc = {k: v.to(device) for k, v in enc.items()}
    with torch.no_grad():
        gen = model.generate(**enc, num_beams=5, max_length=256)
    outs = tok.batch_decode(gen, skip_special_tokens=True, clean_up_tokenization_spaces=True)
    return ip.postprocess_batch(outs, lang=tgt)


which = sys.argv[1] if len(sys.argv) > 1 else "enml"

if which == "enml":
    tok, model = load(EN_ML)
    inputs = ["I need a taxi.", "Where is the nearest hotel?", "How much does this cost?"]
    t0 = time.time()
    outs = translate_batch(model, tok, inputs, "eng_Latn", "mal_Mlym")
    dt = time.time() - t0
    for i, o in zip(inputs, outs):
        print(f"EN: {i}\nML: {o}\n", flush=True)
    print(f"{len(inputs)} sentences in {dt:.1f}s ({dt/len(inputs):.2f}s/sent)", flush=True)
elif which == "mlen":
    tok, model = load(ML_EN)
    inputs = ["എനിക്ക് ഒരു ടാക്സി വേണം.", "അടുത്ത ഹോട്ടല് എവിടെയാണ്?"]
    t0 = time.time()
    outs = translate_batch(model, tok, inputs, "mal_Mlym", "eng_Latn")
    dt = time.time() - t0
    for i, o in zip(inputs, outs):
        print(f"ML: {i}\nEN: {o}\n", flush=True)
    print(f"{len(inputs)} sentences in {dt:.1f}s ({dt/len(inputs):.2f}s/sent)", flush=True)
else:
    raise SystemExit(f"unknown direction {which!r} — use 'enml' or 'mlen'")

print("SMOKE 2", which, "PASSED", flush=True)
