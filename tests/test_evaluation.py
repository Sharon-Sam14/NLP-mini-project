import unittest
from src.evaluation.metrics import calculate_bleu, calculate_exact_match

class TestEvaluationMetrics(unittest.TestCase):
    def test_exact_match(self):
        refs = ["I need a taxi.", "Where is the hotel?"]
        hyps = ["I need a taxi.", "Where is hotel?"]
        acc = calculate_exact_match(hyps, refs)
        self.assertEqual(acc, 50.0)

    def test_bleu_score(self):
        refs = ["I need a taxi to airport"]
        hyps = ["I need a taxi to airport"]
        score = calculate_bleu(hyps, refs)
        self.assertGreater(score, 90.0)

if __name__ == "__main__":
    unittest.main()