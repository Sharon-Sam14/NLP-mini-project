import sys
from pathlib import Path
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, PreTrainedModel
from vendor.IndicTransToolkit.processor import IndicProcessor
from src.config import MODELS_DIR, LANG_EN, LANG_ML

# --- COMPATIBILITY PATCH FOR TRANSFORMERS V5 & INDICTRANS2 ---
if not hasattr(PreTrainedModel, "_tie_or_clone_weights"):
    def _tie_or_clone_weights(self, output_embeddings, input_embeddings):
        """Re-creates the removed HuggingFace internal weight tying helper."""
        if hasattr(output_embeddings, "weight") and hasattr(input_embeddings, "weight"):
            output_embeddings.weight = input_embeddings.weight
        elif isinstance(output_embeddings, torch.nn.Parameter) and isinstance(input_embeddings, torch.nn.Parameter):
            output_embeddings = input_embeddings
        if hasattr(output_embeddings, "bias") and output_embeddings.bias is not None:
            if hasattr(input_embeddings, "bias") and input_embeddings.bias is not None:
                output_embeddings.bias = input_embeddings.bias

    PreTrainedModel._tie_or_clone_weights = _tie_or_clone_weights

_original_post_init = PreTrainedModel.post_init

def _patched_post_init(self, *args, **kwargs):
    cls = self.__class__
    if not hasattr(cls, "_tie_weights_patched_v5"):
        orig_tie = getattr(cls, "tie_weights", None)
        if orig_tie:
            def safe_tie(self_obj, *t_args, **t_kwargs):
                try:
                    return orig_tie(self_obj)
                except TypeError:
                    try:
                        return orig_tie(self_obj, *t_args)
                    except Exception:
                        return None
                except Exception:
                    return None
            cls.tie_weights = safe_tie
        cls._tie_weights_patched_v5 = True
    return _original_post_init(self, *args, **kwargs)

PreTrainedModel.post_init = _patched_post_init
# -------------------------------------------------------------

class TranslationEngine:
    def __init__(self, direction: str = "enml"):
        self.direction = direction
        self.ip = IndicProcessor(inference=True)
        
        if direction == "enml":
            self.model_path = MODELS_DIR / "indictrans2-en-indic-dist-200M"
            self.src_lang = LANG_EN
            self.tgt_lang = LANG_ML
        elif direction == "mlen":
            self.model_path = MODELS_DIR / "indictrans2-indic-en-dist-200M"
            self.src_lang = LANG_ML
            self.tgt_lang = LANG_EN
        else:
            raise ValueError(f"Invalid direction: {direction}")

        self.model = None
        self.tokenizer = None
        self._load_model()

    def _load_model(self):
        if not self.model_path.exists():
            print(f"Warning: Model path {self.model_path} does not exist.")
            return

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path, trust_remote_code=True)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            self.model_path, 
            trust_remote_code=True,
            low_cpu_mem_usage=False
        )

    def translate(self, text: str) -> str:
        if not self.model or not self.tokenizer:
            return "[Error: Model checkpoint not available]"

        batch = self.ip.preprocess_batch([text], src_lang=self.src_lang, tgt_lang=self.tgt_lang)
        inputs = self.tokenizer(batch, truncation=True, padding="longest", return_tensors="pt")

        with torch.no_grad():
            generated_tokens = self.model.generate(
                **inputs,
                min_length=0,
                max_length=256,
                num_beams=5,
                num_return_sequences=1,
            )

        generated_texts = self.tokenizer.batch_decode(
            generated_tokens, skip_special_tokens=True, clean_up_tokenization_spaces=True
        )

        translations = self.ip.postprocess_batch(generated_texts, lang=self.tgt_lang)
        return translations[0] if translations else ""