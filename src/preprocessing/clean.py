import pandas as pd
from pathlib import Path
from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR, RANDOM_SEED

def process_and_split_samanantar():
    raw_file = RAW_DATA_DIR / "samanantar" / "train-00000-of-00004.parquet"
    if not raw_file.exists():
        print(f"Error: Raw file not found at {raw_file}")
        return

    print("Loading raw Samanantar parquet dataset...")
    df = pd.read_parquet(raw_file)
    print(f"Loaded {len(df):,} total sentence pairs.")

    # Drop duplicate pairs
    df = df.drop_duplicates(subset=["src", "tgt"]).reset_index(drop=True)
    print(f"After deduplication: {len(df):,} sentence pairs.")

    # Shuffle with fixed seed for reproducibility
    df = df.sample(frac=1, random_state=RANDOM_SEED).reset_index(drop=True)

    # Calculate 80/10/10 splits
    total = len(df)
    train_end = int(total * 0.8)
    val_end = int(total * 0.9)

    train_df = df.iloc[:train_end]
    val_df = df.iloc[train_end:val_end]
    test_df = df.iloc[val_end:]

    print(f"Splits generated: Train={len(train_df):,}, Validation={len(val_df):,}, Test={len(test_df):,}")

    # Save to data/processed/
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    train_df.to_csv(PROCESSED_DATA_DIR / "train.csv", index=False, encoding="utf-8")
    val_df.to_csv(PROCESSED_DATA_DIR / "val.csv", index=False, encoding="utf-8")
    test_df.to_csv(PROCESSED_DATA_DIR / "test.csv", index=False, encoding="utf-8")

    print(f"Processed CSV files saved successfully in {PROCESSED_DATA_DIR}!")

if __name__ == "__main__":
    process_and_split_samanantar()