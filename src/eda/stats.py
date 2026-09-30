import pandas as pd
from typing import Dict, Any
from src.config import PROCESSED_DATA_DIR
from src.preprocessing.tokenizer import tokenize

def generate_corpus_stats() -> Dict[str, Any]:
    train_file = PROCESSED_DATA_DIR / "train.csv"
    if not train_file.exists():
        raise FileNotFoundError(f"Missing processed data file at {train_file}")

    print("Reading processed training dataset for EDA...")
    df = pd.read_csv(train_file)

    # Word counts per row
    df["src_word_count"] = df["src"].astype(str).apply(lambda x: len(tokenize(x, mode="corpus")))
    df["tgt_word_count"] = df["tgt"].astype(str).apply(lambda x: len(tokenize(x, mode="corpus")))

    stats = {
        "total_pairs": len(df),
        "avg_en_length": float(df["src_word_count"].mean()),
        "avg_ml_length": float(df["tgt_word_count"].mean()),
        "max_en_length": int(df["src_word_count"].max()),
        "max_ml_length": int(df["tgt_word_count"].max()),
    }

    print("\n--- Corpus EDA Statistics ---")
    print(f"Total Sentence Pairs: {stats['total_pairs']:,}")
    print(f"Average English Sentence Length: {stats['avg_en_length']:.2f} words")
    print(f"Average Malayalam Sentence Length: {stats['avg_ml_length']:.2f} words")
    print(f"Max English Length: {stats['max_en_length']} words")
    print(f"Max Malayalam Length: {stats['max_ml_length']} words")

    return stats

if __name__ == "__main__":
    generate_corpus_stats()