# DATASET — AI4Bharat Samanantar (English–Malayalam parallel corpus)

**Status:** raw shard downloaded & verified (2026-09-30). Processed splits and the
tourism dataset are **NOT YET CREATED**. Every number below was measured — nothing estimated.

## Source record

| Field | Value |
|---|---|
| Name | AI4Bharat Samanantar |
| Source URL | https://huggingface.co/datasets/AI4Bharat/Samanantar |
| Config / language pair | `ml` (English → Malayalam) |
| Splits published | `train` only (no official val/test) |
| Total pairs in `ml` (reported by HF API) | 5,924,426 |
| Shards | 4 parquet files under `ml/` — 196,182,916 / 196,177,543 / 196,205,243 / 196,325,606 bytes |
| **Downloaded** | **shard 0 only** (policy: never fetch the full multi-GB corpus) |
| Local path (read-only raw) | `data/raw/samanantar/train-00000-of-00004.parquet` |
| Size (measured) | 196,182,916 bytes — identical to the remote shard size |
| Rows (counted with pandas) | 1,481,107 |
| Columns | `idx` int64 · `src` str (English) · `tgt` str (Malayalam) |
| Content note | subtitle-derived sentences (first row observed to be an English movie-plot sentence) |
| License | **CC-BY-NC-4.0** (non-commercial — keep this in the report) |
| Verified on | 2026-09-30 via HF API `https://huggingface.co/api/datasets/AI4Bharat/Samanantar/tree/main/ml` |

## Re-download (reproducible)

```powershell
hf download AI4Bharat/Samanantar --repo-type dataset `
  --include "ml/train-00000-of-00004.parquet" --local-dir data/raw/samanantar
# hf places it under data/raw/samanantar/ml/ — move to the layout used here:
Move-Item data\raw\samanantar\ml\train-00000-of-00004.parquet data\raw\samanantar\
```

Verify: file must be exactly `196,182,916` bytes; `(Get-Item ...).Length`.

## Rules for this repo

- `data/raw/` is **never overwritten or edited**. All cleaning happens in `data/processed/`.
- Directory separation is strict: `data/raw/` (immutable) · `data/processed/` (splits) · `data/tourism/` (domain set).
- `data/` is **gitignored** (187 MB shard — GitHub rejects files > 100 MB). Provenance lives in this file.

## Planned (NOT YET CREATED)

| Item | Spec | Status |
|---|---|---|
| Train/val/test splits | reproducible **80/10/10, seed 42**, no duplicate sentence pairs leaking across splits; from shard 0 only, sampled to a manageable size (sampling size = decide & record when implementing) | **planned** — will land in `data/processed/{train,validation,test}.csv` with `english, malayalam` columns |
| Dataset inspection stats | row/column counts, empty/duplicate/length/whitespace/Unicode-script analysis (Experiment 1–2 material) | **planned** — notebook `notebooks/01_dataset_analysis.ipynb` |
| Tourism-domain set | 8 categories (hotel, food, transportation, directions, shopping, sightseeing, emergency, general); fields `english, malayalam, category`; extracted from **real parallel pairs only** (never fabricated translations); labeled as verified-source or curated+validated; same 80/10/10 seed-42 split, no cross-split duplicates | **planned** — `data/tourism/` |
| Manglish pairs | for D3/D4 evaluation | **DECISION REQUIRED** (source not yet chosen) |

## Not yet done

- Splits: **NOT YET CREATED** · analysis notebook: **NOT YET CREATED** · tourism set: **NOT YET CREATED**
- Dataset quality analysis numbers: **NOT YET CALCULATED**
- `docs/DATASET.md` must be extended with the *measured* split sizes and dedup counts after sampling runs.
