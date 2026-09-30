import unittest
from src.ner.extractor import detect_category, extract_entities

class TestNERExtractor(unittest.TestCase):
    def test_category_detection(self):
        text = "I need a taxi to the airport."
        category = detect_category(text)
        self.assertEqual(category, "Transportation")

    def test_emergency_detection(self):
        text = "Please help me call a doctor!"
        category = detect_category(text)
        self.assertEqual(category, "Emergency")

    def test_entity_extraction(self):
        text = "Taxi to airport costs ₹500."
        entities = extract_entities(text)
        labels = [e["label"] for e in entities]
        self.assertIn("Money", labels)
        self.assertIn("Transportation", labels)

if __name__ == "__main__":
    unittest.main()