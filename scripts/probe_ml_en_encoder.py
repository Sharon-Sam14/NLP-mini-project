"""Localize the D2 NaN: weights vs encoder call path (ML->EN).

Evidence so far (scripts/probe_ml_en_inputs.py): encoder_outputs reaching
forward are all-NaN -> logits all-NaN -> argmax=0 garbage -> the known issue.
BUT an earlier direct-forward test predicted "I" (p=0.4857) = finite logits.
So this script decides which path is finite:

  A) scan loaded parameters for NaN/Inf (checkpoint corruption?)
  B) standalone encoder call      model.get_encoder()(**enc)
  C) internal encoder (full forward, output_hidden_states=True) -> logits top5
  D) encoder.forward signature (ML->EN vs EN->ML) -> call-contract mismatch?
  E) encoder called with manual inputs_embeds (if signature allows)

Run: python -u scripts/probe_ml_en_encoder.py
"""
import os
import sys
import gc
import inspect
from pathlib import Path

os.chdir(Path(__file__).resolve().parents[1])
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, "vendor")

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from IndicTransToolkit import IndicProcessor

ML_EN = "models/indictrans2-indic-en-dist-200M"
EN_ML = "models/indictrans2-en-indic-dist-200M"


def nan_report(t, tag):
    if not torch.is_tensor(t):
        print(f"  {tag}: not a tensor ({type(t).__name__})", flush=True)
        return
    t32 = t.detach().float()
    n_nan = torch.isnan(t32).sum().item()
    n_inf = torch.isinf(t32).sum().item()
    fin = t32[torch.isfinite(t32)]
    rng = f"[{fin.min().item():.4g}, {fin.max().item():.4g}]" if fin.numel() else "NO FINITE"
    print(f"  {tag}: shape={tuple(t32.shape)} nan={n_nan} inf={n_inf} finite-range={rng}", flush=True)


def scan_params(model, tag):
    bad = []
    n_params = 0
    for name, p in model.named_parameters():
        n_params += 1
        pv = p.detach().float()
        n_nan = torch.isnan(pv).sum().item()
        n_inf = torch.isinf(pv).sum().item()
        if n_nan or n_inf:
            bad.append((name, n_nan, n_inf))
    print(f"  {tag}: {n_params} parameter tensors, {len(bad)} contain NaN/Inf", flush=True)
    for name, n_nan, n_inf in bad[:15]:
        print(f"    ! {name}: nan={n_nan} inf={n_inf}", flush=True)
    return bad


def run_direction(model_dir, tag, src, tgt, sentence, expect_top=None):
    print(f"\n=== {tag}: {model_dir} ===", flush=True)
    tok = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(
        model_dir, trust_remote_code=True, low_cpu_mem_usage=True
    ).eval()
    print(f"  class={type(model).__name__}", flush=True)

    # A) weights NaN?
    scan_params(model, "weights")

    # encoder signature
    enc_mod = model.get_encoder()
    print(f"  encoder class={type(enc_mod).__name__}", flush=True)
    print(f"  encoder.forward{inspect.signature(enc_mod.forward)}", flush=True)

    ip = IndicProcessor(inference=True)
    pre = ip.preprocess_batch([sentence], src, tgt)
    enc = tok(pre, return_tensors="pt", padding=True, truncation=True, max_length=256)
    print(f"  src input_ids={enc['input_ids'].tolist()} "
          f"attn_dtype={enc['attention_mask'].dtype} attn={enc['attention_mask'].tolist()}", flush=True)

    with torch.no_grad():
        # B) standalone encoder
        try:
            eout = enc_mod(**{k: v for k, v in enc.items()})
            hs = eout.last_hidden_state if hasattr(eout, "last_hidden_state") else eout[0]
            nan_report(hs, "B standalone encoder last_hidden_state")
        except Exception as e:  # noqa: BLE001
            print(f"  B standalone FAILED: {type(e).__name__}: {e}", flush=True)
            hs = None

        # C) internal encoder via full forward
        start = torch.tensor([[model.config.decoder_start_token_id]])
        try:
            out = model(
                input_ids=enc["input_ids"],
                attention_mask=enc["attention_mask"],
                decoder_input_ids=start,
                use_cache=False,
                return_dict=True,
                output_hidden_states=True,
            )
            logits = out.logits[0, -1]
            finite = bool(torch.isfinite(logits).all())
            if finite:
                probs = torch.softmax(logits.float(), dim=-1)
                top = torch.topk(probs, 5)
                words = [tok.decode([i]) for i in top.indices.tolist()]
                print(f"  C full forward: logits FINITE, top5="
                      f"{[(w, round(float(p), 4)) for w, p in zip(words, top.values.tolist())]}",
                      flush=True)
            else:
                nan_report(logits, "C full-forward logits")
            ehs = getattr(out, "encoder_hidden_states", None)
            if ehs:
                nan_report(ehs[0], "C internal encoder_hidden_states[0]")
        except Exception as e:  # noqa: BLE001
            print(f"  C full forward FAILED: {type(e).__name__}: {e}", flush=True)

        # E) manual inputs_embeds into encoder (if supported)
        if hs is None or torch.isnan(hs.detach().float()).any():
            try:
                emb_model = model.get_input_embeddings()
                if emb_model is not None:
                    emb = emb_model(enc["input_ids"])
                    nan_report(emb, "E input embeddings")
                    eout2 = enc_mod(inputs_embeds=emb, attention_mask=enc["attention_mask"])
                    hs2 = eout2.last_hidden_state if hasattr(eout2, "last_hidden_state") else eout2[0]
                    nan_report(hs2, "E encoder(inputs_embeds=...)")
                else:
                    print("  E: get_input_embeddings() returned None", flush=True)
            except Exception as e:  # noqa: BLE001
                print(f"  E inputs_embeds FAILED: {type(e).__name__}: {e}", flush=True)

    del model, tok, enc
    gc.collect()


run_direction(ML_EN, "D2 ML->EN", "mal_Mlym", "eng_Latn",
              "എനിക്ക് ഒരു ടാക്സി വേണം.", expect_top="I")
run_direction(EN_ML, "D1 EN->ML (control)", "eng_Latn", "mal_Mlym",
              "I need a taxi.")

print("\nprobe done", flush=True)
