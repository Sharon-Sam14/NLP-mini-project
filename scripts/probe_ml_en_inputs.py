"""Probe what transformers v5 generate() actually feeds the D2 model.

Known issue: direct forward predicts "I" correctly, but generate() returns
[2,0,0,...] (greedy) / [2,8] (beam). This script:
  1) dumps prepare_inputs_for_generation output (fresh cache case)
  2) hooks model.forward to print every call's inputs during greedy generate
  3) traces the Cache<->tuple bridge entry point
  4) retries greedy with use_cache=False
  5) manual loop with the correct decoder_input_ids kwarg

Run: python -u scripts/probe_ml_en_inputs.py
"""
import os
import sys
from pathlib import Path

os.chdir(Path(__file__).resolve().parents[1])
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, "vendor")

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from transformers.cache_utils import DynamicCache, EncoderDecoderCache

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
print("src input_ids:", enc["input_ids"].tolist(), flush=True)


def brief(v):
    if hasattr(v, "shape"):
        return f"tensor{tuple(v.shape)}"
    if v is None:
        return "None"
    if isinstance(v, (list, tuple)):
        return f"{type(v).__name__}[len={len(v)}]"
    return repr(v)[:110]


# ---- 1) what does the custom prepare return? ----
with torch.no_grad():
    enc_out = model.get_encoder()(**{k: v for k, v in enc.items()})
    fresh = EncoderDecoderCache(DynamicCache(), DynamicCache())
    prep = model.prepare_inputs_for_generation(
        torch.tensor([[model.config.decoder_start_token_id]]),
        past_key_values=fresh,
        attention_mask=enc["attention_mask"],
        use_cache=True,
        encoder_outputs=enc_out,
    )
    print("PREPARE ->", {k: brief(v) for k, v in prep.items()}, flush=True)

# ---- 2) hook forward + 3) trace bridge ----
orig_forward = model.forward
orig_bridge = model._cache_to_legacy_past
counter = {"n": 0}


def hooked(*args, **kwargs):
    counter["n"] += 1
    if counter["n"] <= 3:
        print(f"FORWARD#{counter['n']} posargs={len(args)}",
              {k: brief(v) for k, v in kwargs.items()}, flush=True)
    return orig_forward(*args, **kwargs)


def bridge_dbg(cache):
    r = orig_bridge(cache)
    out = "None" if r is None else type(r).__name__
    extra = ""
    if isinstance(cache, EncoderDecoderCache):
        sc, cc = cache.self_attention_cache, cache.cross_attention_cache
        extra = f" sc_layers={len(sc.layers)} sc_init={[l.is_initialized for l in sc.layers]}" \
                f" cc_layers={len(cc.layers)} cc_init={[l.is_initialized for l in cc.layers]}"
    print(f"BRIDGE in={type(cache).__name__} out={out}{extra}", flush=True)
    return r


model.forward = hooked
model._cache_to_legacy_past = bridge_dbg

with torch.no_grad():
    # ---- 4) greedy with cache (current behavior) ----
    a = model.generate(**enc, num_beams=1, max_new_tokens=8, do_sample=False)
    print("A  greedy+cache  :", a[0].tolist(), flush=True)

    # ---- 4b) greedy WITHOUT cache ----
    b = model.generate(**enc, num_beams=1, max_new_tokens=8, do_sample=False, use_cache=False)
    print("B  greedy-nocache:", b[0].tolist(), flush=True)

model.forward = orig_forward
model._cache_to_legacy_past = orig_bridge

# ---- 5) manual loop, correct kwarg ----
with torch.no_grad():
    dec = torch.tensor([[model.config.decoder_start_token_id]])
    past = None
    for _step in range(8):
        out = model(
            decoder_input_ids=dec if past is None else dec[:, -1:],
            encoder_outputs=enc_out,
            past_key_values=past,
            use_cache=True,
            return_dict=True,
        )
        nxt = out.logits[:, -1].argmax(dim=-1, keepdim=True)
        past = out.past_key_values
        dec = torch.cat([dec, nxt], dim=-1)
        if nxt.item() == model.config.eos_token_id:
            break
    print("C  manual+cache  :", dec[0].tolist(),
          "decoded=", tok.decode(dec[0], skip_special_tokens=True), flush=True)

print("probe done", flush=True)
