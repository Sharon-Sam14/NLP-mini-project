import unittest
from src.patterns.regex import extract_regex_entities

class TestRegexPatterns(unittest.TestCase):
    def test_price_extraction(self):
        text = "The hotel room costs ₹2500 per night."
        entities = extract_regex_entities(text)
        self.assertTrue(any(e["label"] == "Money" and "2500" in e["text"] for e in entities))

    def test_phone_extraction(self):
        text = "Call the taxi driver at +91 9847012345 for booking."
        entities = extract_regex_entities(text)
        self.assertTrue(any(e["label"] == "Phone" for e in entities))

if __name__ == "__main__":
    unittest.main()