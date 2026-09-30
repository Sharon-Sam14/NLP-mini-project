import re
from typing import List
from .text_ops import preprocess_text

# Regex pattern matching words (both Malayalam script & Latin/ASCII)
WORD_TOKEN_PATTERN = re.compile(r"[\u0D00-\u0D7F\w]+", re.UNICODE)

def tokenize(text: str, mode: str = "translation") -> List[str]:
    """
    Tokenizes Malayalam / English text.
    - mode="translation": Preserves original casing and lighter filtering.
    - mode="corpus": Lowercases Latin characters for vocabulary analysis/EDA.
    """
    text = preprocess_text(text, lower_latin=(mode == "corpus"))
    tokens = WORD_TOKEN_PATTERN.findall(text)
    return tokens

def word_count(text: str) -> int:
    """Returns the total number of word tokens in a string."""
    return len(tokenize(text))