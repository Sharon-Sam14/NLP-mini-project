import re

# Simple mapping rule table for Malayalam to Romanized Manglish
ML_TO_MG_MAP = {
    "എനിക്ക്": "enikku",
    "ഒരു": "oru",
    "ടാക്സി": "taxi",
    "വേണം": "venam",
    "ഹോട്ടൽ": "hotel",
    "എവിടെ": "evide",
    "സഹായം": "sahayam",
    "ഭക്ഷണം": "bhakshanam",
}

def malayalam_to_manglish(text: str) -> str:
    """Converts Malayalam text into Romanized Manglish."""
    words = text.split()
    converted = [ML_TO_MG_MAP.get(w, w) for w in words]
    return " ".join(converted)

def manglish_to_malayalam(text: str) -> str:
    """Normalizes Manglish text into Malayalam script."""
    words = text.lower().split()
    reverse_map = {v: k for k, v in ML_TO_MG_MAP.items()}
    converted = [reverse_map.get(w, w) for w in words]
    return " ".join(converted)