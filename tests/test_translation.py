import unittest
from src.translation.engine import TranslationEngine

class TestTranslationEngine(unittest.TestCase):
    def test_enml_translation(self):
        engine = TranslationEngine(direction="enml")
        if engine.model is not None:
            result = engine.translate("I need a taxi.")
            self.assertIsInstance(result, str)
            self.assertTrue(len(result) > 0)
        else:
            self.skipTest("Model weights not available locally.")

if __name__ == "__main__":
    unittest.main()