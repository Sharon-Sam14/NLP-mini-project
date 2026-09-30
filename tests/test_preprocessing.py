import unittest
from src.preprocessing.text_ops import normalize_unicode, preprocess_text
from src.preprocessing.tokenizer import tokenize

class TestPreprocessing(unittest.TestCase):
    def test_unicode_roundtrip(self):
        sample = "എനിക്ക് ഒരു ടാക്സി വേണം."
        normalized = normalize_unicode(sample)
        self.assertEqual(sample, normalized)

    def test_whitespace_cleaning(self):
        sample = "  എനിക്ക്   ഒരു   ടാക്സി   "
        expected = "എനിക്ക് ഒരു ടാക്സി"
        self.assertEqual(preprocess_text(sample), expected)

    def test_tokenization(self):
        sample = "I need a taxi to the airport."
        tokens = tokenize(sample)
        self.assertIn("taxi", tokens)
        self.assertEqual(len(tokens), 7)

if __name__ == "__main__":
    unittest.main()
    