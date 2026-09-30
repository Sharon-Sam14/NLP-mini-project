"""Diagnose the ML->EN KNOWN ISSUE (see docs/MODEL.md).

Symptom: Malayalam -> English model.generate() returns junk (single token "to").
Evidence so far that the WEIGHTS and TOKENIZATION are good (measured 2026-09-30):
  - 228,316,160 parameters — exactly the official count
  - tensor names identical to the working EN->ML checkpoint
  - input tokenization: 0 <unk>, dict sizes match config (SRC 122706 / TGT 32296)
  - a DIRECT forward pass predicts the correct first token: "I" (p=0.4857),
    with "taxi" also in the top-10

So the bug is in the generate() path (custom prepare_inputs_for_generation /
transformers-v5 KV-cache bridge in models/indictrans2-indic-en-dist-200M/
modeling_indictrans.py), not in the model itself.

This script compares three decoding paths on one sentence:
    A) greedy generate (num_beams=1)
    B) beam-5 generate (what evaluation will use)
    C) manual greedy loop feeding outputs.past_key_values back
       (exercises the Cache<->legacy-tuple bridge step by step)

Run:  python -u scripts/diagnose_ml_en.py
Expected: find the first step where a path diverges from the correct "I ..." start.
"""
import os
import sys
from pathlib import Path

os.chdir(Path(__file__).resolve().parents[1])  # repo root
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # Windows console is cp1252
sys.path.insert(0, "vendor")

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from IndicTransToolkit import IndicProcessor

ML_EN = "models/indictrans2-indic-en-dist-200M"
ip = IndicProcessor(inference=True)
tok = AutoTokenizer.from_pretrained(ML_EN, trust_remote_code=True)
model = AutoModelForSeq2SeqLM.from_pretrained(
    ML_EN, trust_remote_code=True, low_cpu_mem_usage=True
).eval()

ml = ["എനിക്ക് ഒരു ടാക്സി വേണം."]
pre = ip.preprocess_batch(ml, "mal_Mlym", "eng_Latn")
enc = tok(pre, return_tensors="pt", padding=True, truncation=True, max_length=256)


def show(tag, seq):
    ids = seq.tolist()
    print(f"{tag}: ids={ids} decoded={tok.decode(ids, skip_special_tokens=True)!r}", flush=True)


with torch.no_grad():
    # A: greedy
    a = model.generate(**enc, num_beams=1, max_new_tokens=15, do_sample=False)
    show("A greedy ", a[0])

    # B: beam 5 (same settings as scripts/smoke_translate.py)
    b = model.generate(**enc, num_beams=5, max_new_tokens=15)
    show("B beam5  ", b[0])

    # C: manual greedy loop, feeding past_key_values back (exercises the bridge)
    dec = torch.tensor([[model.config.decoder_start_token_id]])
    past = None
    for _step in range(10):
        out = model(
            input_ids=dec if past is None else dec[:, -1:],
            encoder_outputs=model.get_encoder()(**{k: v for k, v in enc.items()}),
            past_key_values=past,
            use_cache=True,
            return_dict=True,
        )
        nxt = out.logits[:, -1].argmax(dim=-1, keepdim=True)
        past = out.past_key_values
        dec = torch.cat([dec, nxt], dim=-1)
        if nxt.item() == model.config.eos_token_id:
            break
    show("C manual ", dec[0])

print("diag done — compare: which path first diverges from the correct 'I ...' start?", flush=True)
