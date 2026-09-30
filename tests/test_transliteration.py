import unittest
from src.transliteration.ml_to_mg import malayalam_to_manglish, manglish_to_malayalam

class TestTransliteration(unittest.TestCase):
    def test_ml_to_mg(self):
        text = "എനിക്ക് ഒരു ടാക്സി വേണം"
        result = malayalam_to_manglish(text)
        self.assertEqual(result, "enikku oru taxi venam")

    def test_mg_to_ml(self):
        text = "enikku oru taxi venam"
        result = manglish_to_malayalam(text)
        self.assertEqual(result, "എനിക്ക് ഒരു ടാക്സി വേണം")

if __name__ == "__main__":
    unittest.main()