import re
from typing import List, Dict, Any

# Pattern definitions
CURRENCY_PATTERN = re.compile(
    r"(?:₹|Rs\.?|INR)\s?\d+(?:,\d+)*(?:\.\d+)?|\d+(?:,\d+)*(?:\.\d+)?\s?(?:rupees|INR|Rs)",
    re.IGNORECASE,
)
PHONE_PATTERN = re.compile(
    r"(?:\+91[\-\s]?)?[6-9]\d{9}|0\d{2,4}[\-\s]?\d{6,8}"
)
URL_PATTERN = re.compile(
    r"https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
)
DATE_PATTERN = re.compile(
    r"\b(?:\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}|\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})\b",
    re.IGNORECASE,
)

def extract_regex_entities(text: str) -> List[Dict[str, Any]]:
    """Extracts regex-based entity patterns (Prices, Phone, URLs, Dates) with spans."""
    entities = []

    for match in CURRENCY_PATTERN.finditer(text):
        entities.append({"text": match.group(), "label": "Money", "start": match.start(), "end": match.end()})

    for match in PHONE_PATTERN.finditer(text):
        entities.append({"text": match.group(), "label": "Phone", "start": match.start(), "end": match.end()})

    for match in URL_PATTERN.finditer(text):
        entities.append({"text": match.group(), "label": "URL", "start": match.start(), "end": match.end()})

    for match in DATE_PATTERN.finditer(text):
        entities.append({"text": match.group(), "label": "Date", "start": match.start(), "end": match.end()})

    return entities
