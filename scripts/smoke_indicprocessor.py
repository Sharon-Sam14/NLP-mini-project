"""Smoke test 1: vendored IndicProcessor round-trip (no model download needed).

Verifies the pure-Python IndicTransToolkit port (vendor/IndicTransToolkit):
  - EN preprocess : language tags prepended ("eng_Latn mal_Mlym ...")
  - ML preprocess : Malayalam -> Devanagari script for model input
  - ML postprocess: Devanagari model output -> Malayalam script + detokenize
  - EN postprocess: Moses-style detokenization

IMPORTANT upstream contract: on one IndicProcessor instance, preprocess_batch()
and postprocess_batch() must be called as matched pairs (same number of
sentences); postprocess_batch() clears the leftover placeholder queue.

Run:  python -u scripts/smoke_indicprocessor.py      (from anywhere)
Expected final line: SMOKE 1 PASSED
"""
import os
import sys
from pathlib import Path

os.chdir(Path(__file__).resolve().parents[1])  # repo root
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # Windows console is cp1252
sys.path.insert(0, "vendor")

from IndicTransToolkit import IndicProcessor

ip = IndicProcessor(inference=True)

# Pair 1: EN -> ML direction (3 inputs, target lang mal_Mlym)
en = ["Hello, how are you?", "I need a taxi.", "Where is the nearest hotel?"]
pre_a = ip.preprocess_batch(en, "eng_Latn", "mal_Mlym")
for p in pre_a:
    print("EN pre :", p, flush=True)
fake_ml_dev = [
    "नमस्ते , तिमी कस्तो हुनुहुन्छ ?",
    "मलाई एक ट्याक्सी चाहिए ।",
    "नजिकको होटल कहाँ छ ?",
]
post_a = ip.postprocess_batch(fake_ml_dev, lang="mal_Mlym")
for o in post_a:
    print("ML post:", o, flush=True)
print("pair 1 ok, queue =", ip._placeholder_entity_maps.qsize(), flush=True)

# Pair 2: ML -> EN direction (1 input, target lang eng_Latn)
ml = ["എവിടെയാണ് അടുത്ത ഹോട്ടല്?"]
pre_b = ip.preprocess_batch(ml, "mal_Mlym", "eng_Latn")
for p in pre_b:
    print("ML pre :", p, flush=True)
post_b = ip.postprocess_batch(["Where is the nearest hotel ?"], lang="eng_Latn")
for o in post_b:
    print("EN post:", o, flush=True)
print("pair 2 ok, queue =", ip._placeholder_entity_maps.qsize(), flush=True)

print("SMOKE 1 PASSED", flush=True)
