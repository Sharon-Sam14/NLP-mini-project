import unittest
from src.ngram.builder import NGramModel

class TestNGramModel(unittest.TestCase):
    def test_bigram_prediction(self):
        corpus = [
            "need a taxi to airport",
            "need a hotel room",
            "need a taxi to railway station"
        ]
        model = NGramModel(n=2)
        model.train(corpus)

        predictions = model.predict_next(["need"], top_k=1)
        self.assertEqual(predictions[0][0], "a")

    def test_trigram_prediction(self):
        corpus = [
            "need a taxi to airport",
            "need a hotel room",
            "need a taxi to railway station"
        ]
        model = NGramModel(n=3)
        model.train(corpus)

        predictions = model.predict_next(["need", "a"], top_k=1)
        self.assertEqual(predictions[0][0], "taxi")

if __name__ == "__main__":
    unittest.main()