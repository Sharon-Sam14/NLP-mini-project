import unicodedata
import re

def normalize_unicode(text: str) -> str:
    """Applies Unicode NFC normalization to preserve Malayalam glyph integrity."""
    if not isinstance(text, str):
        return ""
    return unicodedata.normalize("NFC", text)

def clean_whitespace(text: str) -> str:
    """Collapses consecutive whitespace characters into a single space and trims edges."""
    return re.sub(r"\s+", " ", text).strip()

def preprocess_text(text: str, lower_latin: bool = False) -> str:
    """
    Applies Unicode normalization and whitespace cleaning.
    Only lowercases English/Latin scripts—never Malayalam!
    """
    text = normalize_unicode(text)
    text = clean_whitespace(text)
    if lower_latin:
        # Lowercase English characters while leaving Malayalam characters intact
        text = "".join([c.lower() if c.isascii() else c for c in text])
    return text