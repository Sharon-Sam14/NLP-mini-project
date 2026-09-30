from typing import List, Dict
from src.preprocessing.tokenizer import tokenize

# Gloss inventory for tourism-relevant ambiguous words
SENSE_INVENTORY: Dict[str, Dict[str, str]] = {
    "room": {
        "hotel": "a bedroom in a hotel or inn for tourist stay",
        "space": "an unoccupied area or capacity inside a vehicle or container"
    },
    "charge": {
        "fee": "the price or fee required for a service or ticket",
        "battery": "to store electrical energy in a device or phone"
    },
    "bank": {
        "financial": "an institution for receiving keeping and lending money",
        "river": "the sloping land along the side of a river or lake"
    }
}

def simplified_lesk(word: str, sentence: str) -> str:
    """
    Applies Lesk-style overlap scoring between sentence context and sense definitions.
    Returns the sense key with the highest overlap.
    """
    word_lower = word.lower()
    if word_lower not in SENSE_INVENTORY:
        return "default"

    context_tokens = set(tokenize(sentence, mode="corpus"))
    senses = SENSE_INVENTORY[word_lower]
    
    best_sense = list(senses.keys())[0]
    max_overlap = -1

    for sense_key, gloss in senses.items():
        gloss_tokens = set(tokenize(gloss, mode="corpus"))
        overlap = len(context_tokens.intersection(gloss_tokens))
        
        if overlap > max_overlap:
            max_overlap = overlap
            best_sense = sense_key

    return best_sense