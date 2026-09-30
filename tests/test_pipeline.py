import unittest
from src.pipeline.directions import TranslationPipeline

class TestTranslationPipeline(unittest.TestCase):
    def setUp(self):
        self.pipeline = TranslationPipeline()

    def test_pipeline_structure(self):
        result = self.pipeline.translate("I need a taxi to airport.", direction="D1")
        self.assertIn("translated_text", result)
        self.assertEqual(result["category"], "Transportation")
        self.assertIn("entities", result)

if __name__ == "__main__":
    unittest.main()