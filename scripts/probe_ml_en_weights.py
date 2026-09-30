"""D2 weight-magnitude probe: corrupt checkpoint vs bad loading?

Findings so far: D2 weights contain no NaN/Inf, but internal encoder output
range is ~1e37 (explodes -> NaN logits). Hypotheses:
  H1: the mirror's pytorch_model.bin itself contains garbage tensors
  H2: loading with low_cpu_mem_usage=True leaves some tensors unfilled
      (torch.empty garbage) — e.g. tied-weight handling
  H3: weights normal, encoder code explodes

Checks:
  1) raw bin file: per-tensor max-abs (flag > 10)
  2) loaded model (low_cpu_mem_usage=True): max-abs per tensor
  3) loaded model (low_cpu_mem_usage=False): max-abs + standalone encoder
  4) standalone encoder layer-by-layer (output_hidden_states) if still broken

Run: python -u scripts/probe_ml_en_weights.py
"""
import os
import sys
import gc
from pathlib import Path

os.chdir(Path(__file__).resolve().parents[1])
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, "vendor")

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from IndicTransToolkit import IndicProcessor

ML_EN = "models/indictrans2-indic-en-dist-200M"
BIN = Path(ML_EN) / "pytorch_model.bin"
FLAG = 10.0  # abs values above this are suspicious for transformer weights


def maxabs_report(named_tensors, tag, limit=20):
    offenders = []
    for name, t in named_tensors:
        if not torch.is_tensor(t) or t.numel() == 0:
            continue
        tv = t.detach().float()
        m = tv.abs().max().item() if torch.isfinite(tv).any() else float("inf")
        if m > FLAG:
            offenders.append((name, m, tv.abs().median().item()))
    offenders.sort(key=lambda x: -x[1])
    print(f"  {tag}: {len(offenders)} tensors with max|w| > {FLAG}", flush=True)
    for name, mx, med in offenders[:limit]:
        print(f"    ! {name}: max={mx:.4g} median={med:.4g}", flush=True)
    return offenders


# ---------- 1) raw checkpoint file ----------
print("=== 1) raw pytorch_model.bin ===", flush=True)
sd = torch.load(BIN, map_location="cpu", weights_only=True)
print(f"  keys={len(sd)} file={BIN.stat().st_size} bytes", flush=True)
maxabs_report(sd.items(), "raw bin")

# ---------- 2) loaded model, low_cpu_mem_usage=True ----------
print("=== 2) loaded model low_cpu_mem_usage=True ===", flush=True)
m1 = AutoModelForSeq2SeqLM.from_pretrained(
    ML_EN, trust_remote_code=True, low_cpu_mem_usage=True
).eval()
maxabs_report(m1.named_parameters(), "loaded(True)")
del m1
gc.collect()

# ---------- 3) loaded model, low_cpu_mem_usage=False + encoder test ----------
print("=== 3) loaded model low_cpu_mem_usage=False ===", flush=True)
m2 = AutoModelForSeq2SeqLM.from_pretrained(
    ML_EN, trust_remote_code=True, low_cpu_mem_usage=False
).eval()
maxabs_report(m2.named_parameters(), "loaded(False)")

ip = IndicProcessor(inference=True)
tok = AutoTokenizer.from_pretrained(ML_EN, trust_remote_code=True)
pre = ip.preprocess_batch(["എനിക്ക് ഒരു ടാക്സി വേണം."], "mal_Mlym", "eng_Latn")
enc = tok(pre, return_tensors="pt", padding=True, truncation=True, max_length=256)

with torch.no_grad():
    eout = m2.get_encoder()(**{k: v for k, v in enc.items()})
    hs = eout.last_hidden_state if hasattr(eout, "last_hidden_state") else eout[0]
    fin = hs[torch.isfinite(hs)]
    print(f"  encoder standalone: shape={tuple(hs.shape)} nan={torch.isnan(hs).sum().item()} "
          f"range=[{fin.min().item():.4g},{fin.max().item():.4g}]" if fin.numel()
          else f"  encoder standalone: shape={tuple(hs.shape)} NO FINITE", flush=True)

    # ---------- 4) layer-by-layer if still broken ----------
    if torch.isnan(hs).any() or hs.shape[1] != enc["input_ids"].shape[1]:
        try:
            eout2 = m2.get_encoder()(
                input_ids=enc["input_ids"], attention_mask=enc["attention_mask"],
                output_hidden_states=True, return_dict=True,
            )
            for i, layer_hs in enumerate(eout2.hidden_states):
                lfin = layer_hs[torch.isfinite(layer_hs)]
                rng = (f"[{lfin.min().item():.4g},{lfin.max().item():.4g}]"
                       if lfin.numel() else "NO FINITE")
                print(f"    hidden[{i}] shape={tuple(layer_hs.shape)} "
                      f"nan={torch.isnan(layer_hs).sum().item()} {rng}", flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"    layerwise FAILED: {type(e).__name__}: {e}", flush=True)

    # internal path for comparison
    out = m2(
        input_ids=enc["input_ids"], attention_mask=enc["attention_mask"],
        decoder_input_ids=torch.tensor([[m2.config.decoder_start_token_id]]),
        use_cache=False, return_dict=True, output_hidden_states=True,
    )
    ehs = out.encoder_hidden_states[0]
    fin2 = ehs[torch.isfinite(ehs)]
    print(f"  internal encoder: shape={tuple(ehs.shape)} nan={torch.isnan(ehs).sum().item()} "
          f"range=[{fin2.min().item():.4g},{fin2.max().item():.4g}]" if fin2.numel()
          else f"  internal encoder: NO FINITE", flush=True)
    logits = out.logits[0, -1]
    if torch.isfinite(logits).all():
        top = torch.topk(torch.softmax(logits, -1), 5)
        print("  internal logits top5:",
              [(tok.decode([i]), round(float(p), 4))
               for i, p in zip(top.indices.tolist(), top.values.tolist())], flush=True)
    else:
        print(f"  internal logits: nan={torch.isnan(logits).sum().item()}/{logits.numel()}", flush=True)

del m2, sd
gc.collect()
print("probe done", flush=True)
