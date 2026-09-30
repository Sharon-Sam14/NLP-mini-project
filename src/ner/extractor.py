import re
from typing import List, Dict, Any
from src.patterns.regex import extract_regex_entities

# Tourism keyword dictionary for rule-based category & chunk detection
TOURISM_KEYWORDS = {
    "Hotel / Accommodation": ["hotel", "resort", "room", "stay", "booking", "homestay", "lodge", "ഹോട്ടൽ", "റൂം"],
    "Food / Restaurant": ["restaurant", "food", "dish", "spicy", "menu", "tea", "coffee", "breakfast", "dinner", "ഭക്ഷണം"],
    "Transportation": ["taxi", "cab", "bus", "train", "airport", "railway", "auto", "driver", " ferry", "ടാക്സി", "ബസ്"],
    "Directions": ["where", "map", "near", "distance", "route", "left", "right", "way", "എവിടെ"],
    "Shopping": ["price", "cost", "buy", "shop", "saree", "market", "rupees", "വാങ്ങാൻ"],
    "Sightseeing": ["beach", "temple", "boating", "waterfall", "park", "tour", "view", "കാണാൻ"],
    "Emergency": ["doctor", "hospital", "police", "help", "help!", "emergency", "ആശുപത്രി", "സഹായം"],
}

def detect_category(text: str) -> str:
    """Detects the primary tourism category based on keyword matches."""
    text_lower = text.lower()
    scores = {category: 0 for category in TOURISM_KEYWORDS}

    for category, keywords in TOURISM_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                scores[category] += 1

    best_category = max(scores, key=scores.get)
    return best_category if scores[best_category] > 0 else "General Conversation"

def extract_entities(text: str) -> List[Dict[str, Any]]:
    """Merges regex extraction with keyword chunking to return typed entities."""
    entities = extract_regex_entities(text)
    
    # Custom keyword chunking for Location/Transport/Hotel entities
    text_lower = text.lower()
    for category, keywords in TOURISM_KEYWORDS.items():
        for kw in keywords:
            for match in re.finditer(re.escape(kw), text_lower):
                entities.append({
                    "text": match.group(),
                    "label": category.split(" / ")[0],
                    "start": match.start(),
                    "end": match.end()
                })
    return entities