from pathlib import Path

# Base Paths
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
TOURISM_DATA_DIR = DATA_DIR / "tourism"
TEST_DATA_DIR = DATA_DIR / "test"
MODELS_DIR = ROOT_DIR / "models"
REPORTS_DIR = ROOT_DIR / "reports"

# Seed & Reproducibility
RANDOM_SEED = 42

# Tourism Categories (FR-5)
TOURISM_CATEGORIES = [
    "Hotel / Accommodation",
    "Food / Restaurant",
    "Transportation",
    "Directions",
    "Shopping",
    "Sightseeing",
    "Emergency",
    "General Conversation",
]

# Language Identifiers
LANG_EN = "eng_Latn"
LANG_ML = "mal_Mlym"