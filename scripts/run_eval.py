import pandas as pd
from pathlib import Path
from src.config import PROCESSED_DATA_DIR, REPORTS_DIR
from src.pipeline.directions import TranslationPipeline
from src.evaluation.metrics import calculate_bleu, calculate_exact_match, measure_latency

def run_evaluation(sample_size: int = 50):
    test_file = PROCESSED_DATA_DIR / "test.csv"
    if not test_file.exists():
        print(f"Error: Frozen test dataset not found at {test_file}")
        return

    print(f"Loading frozen test set ({test_file})...")
    df = pd.read_csv(test_file).head(sample_size)
    
    pipeline = TranslationPipeline()
    
    english_refs = df["src"].astype(str).tolist()
    malayalam_refs = df["tgt"].astype(str).tolist()

    print(f"Running evaluation on {len(df)} test samples...")

    # Evaluate D1: English -> Malayalam
    d1_hypotheses = []
    for text in english_refs:
        res = pipeline.translate(text, direction="D1")
        d1_hypotheses.append(res["translated_text"])

    d1_bleu = calculate_bleu(d1_hypotheses, malayalam_refs)
    d1_em = calculate_exact_match(d1_hypotheses, malayalam_refs)

    # Measure Latency
    sample_sentence = "I need a taxi to the airport."
    latency = measure_latency(pipeline.translate, sample_sentence, direction="D1", repetitions=3)

    # Display & Save Report
    print("\n================ EVALUATION REPORT ================")
    print(f"D1 (EN -> ML) BLEU Score : {d1_bleu:.2f}")
    print(f"D1 (EN -> ML) Exact Match: {d1_em:.2f}%")
    print(f"Average Pipeline Latency : {latency:.3f} seconds/sentence")
    print("====================================================")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_file = REPORTS_DIR / "evaluation_report.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("=== Evaluation Summary ===\n")
        f.write(f"Evaluated Samples: {len(df)}\n")
        f.write(f"D1 BLEU Score: {d1_bleu:.2f}\n")
        f.write(f"D1 Exact Match: {d1_em:.2f}%\n")
        f.write(f"Latency: {latency:.3f}s\n")

    print(f"Report saved to {report_file}")

if __name__ == "__main__":
    run_evaluation()