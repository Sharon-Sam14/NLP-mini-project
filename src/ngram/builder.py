from collections import defaultdict, Counter
from typing import List, Tuple
from src.preprocessing.tokenizer import tokenize

class NGramModel:
    def __init__(self, n: int = 2):
        self.n = n
        self.counts = defaultdict(Counter)

    def train(self, sentences: List[str]):
        """Trains the N-gram model by building word frequency counts."""
        for sentence in sentences:
            tokens = tokenize(sentence, mode="corpus")
            if len(tokens) < self.n:
                continue
            for i in range(len(tokens) - self.n + 1):
                context = tuple(tokens[i : i + self.n - 1])
                next_word = tokens[i + self.n - 1]
                self.counts[context][next_word] += 1

    def predict_next(self, context: List[str], top_k: int = 3) -> List[Tuple[str, int]]:
        """Returns the top_k most likely next words given a preceding context."""
        ctx = tuple(context[-(self.n - 1) :])
        if ctx not in self.counts:
            return []
        return self.counts[ctx].most_common(top_k)