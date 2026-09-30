import time
from typing import List, Dict, Any
import sacrebleu

def calculate_bleu(hypotheses: List[str], references: List[str]) -> float:
    """Calculates corpus-level BLEU score using SacreBLEU."""
    if not hypotheses or not references:
        return 0.0
    # SacreBLEU expects a list of reference lists
    bleu = sacrebleu.corpus_bleu(hypotheses, [references])
    return float(bleu.score)

def calculate_exact_match(hypotheses: List[str], references: List[str]) -> float:
    """Calculates exact/acceptable phrase match accuracy percentage."""
    if not hypotheses or not references:
        return 0.0
    matches = sum(1 for h, r in zip(hypotheses, references) if h.strip().lower() == r.strip().lower())
    return (matches / len(references)) * 100.0

def measure_latency(pipeline_func, sample_text: str, direction: str, repetitions: int = 5) -> float:
    """Measures average execution time per direction call in seconds."""
    times = []
    for _ in range(repetitions):
        start = time.perf_counter()
        pipeline_func(sample_text, direction=direction)
        end = time.perf_counter()
        times.append(end - start)
    return float(sum(times) / len(times))