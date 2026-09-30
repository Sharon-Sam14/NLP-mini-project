from typing import Dict, Any
from src.translation.engine import TranslationEngine
from src.transliteration.ml_to_mg import malayalam_to_manglish, manglish_to_malayalam
from src.ner.extractor import detect_category, extract_entities

class TranslationPipeline:
    def __init__(self):
        # Lazy loading or fallback engine initialization
        self.engine_enml = None
        self.engine_mlen = None

    def _get_enml_engine(self):
        if self.engine_enml is None:
            self.engine_enml = TranslationEngine(direction="enml")
        return self.engine_enml

    def _get_mlen_engine(self):
        if self.engine_mlen is None:
            self.engine_mlen = TranslationEngine(direction="mlen")
        return self.engine_mlen

    def translate(self, text: str, direction: str) -> Dict[str, Any]:
        """
        Main routing function for D1, D2, D3, D4.
        Returns a dictionary with translated_text, category, and entities.
        """
        category = detect_category(text)
        entities = extract_entities(text)
        translated_text = ""

        if direction == "D1":  # English -> Malayalam
            engine = self._get_enml_engine()
            translated_text = engine.translate(text)

        elif direction == "D2":  # Malayalam -> English
            engine = self._get_mlen_engine()
            translated_text = engine.translate(text)

        elif direction == "D3":  # Manglish -> English
            ml_text = manglish_to_malayalam(text)
            engine = self._get_mlen_engine()
            translated_text = engine.translate(ml_text)

        elif direction == "D4":  # English -> Manglish
            engine = self._get_enml_engine()
            ml_text = engine.translate(text)
            translated_text = malayalam_to_manglish(ml_text)

        else:
            raise ValueError(f"Invalid direction: {direction}")

        return {
            "source_text": text,
            "direction": direction,
            "translated_text": translated_text,
            "category": category,
            "entities": entities,
        }