"""Apply transformers-v5 compatibility patches to local IndicTrans2 copies.

The upstream IndicTrans2 HF code was written for transformers 4.x; this
machine has transformers 5.12.1. All patches are mechanical and
inference-neutral (no model logic, weights, or tokenization changes):

configuration_indictrans.py  (both copies)
  - `transformers.onnx` was removed in v5; wrapped in try/except with a
    stub (ONNX export is never used in this project).

tokenization_indictrans.py  (both copies)
  - v5 forbids assigning special tokens before super().__init__();
    __init__ reordered: unwrap tokens locally -> load/validate vocabs ->
    super().__init__() -> switch mode -> cache token ids.

modeling_indictrans.py  (the two copies come from different export dates,
                         so each patch declares variants)
  - tie_weights() must accept v5's keyword arguments.
  - newer export: v5 removed _tie_or_clone_weights -> tie by directly
    sharing the Parameter (same dst<-src direction as v4).
  - older export: must inherit GenerationMixin explicitly (v5 removed it
    from PreTrainedModel) or model.generate() is unavailable.

Re-run this script after re-downloading the checkpoints.
"""
import io
import pathlib

PATCHES = {}


def add_patch(fname, old, new, required=True):
    PATCHES.setdefault(fname, []).append((old, new, required))


add_patch(
    "configuration_indictrans.py",
    "from transformers.onnx import OnnxConfig, OnnxSeq2SeqConfigWithPast\n"
    "from transformers.onnx.utils import compute_effective_axis_dimension",
    """try:  # transformers >= 5 removed transformers.onnx; ONNX export unused here
    from transformers.onnx import OnnxConfig, OnnxSeq2SeqConfigWithPast
    from transformers.onnx.utils import compute_effective_axis_dimension
except ImportError:
    class OnnxConfig:
        default_fixed_batch = 2
        default_fixed_sequence = 8

    class OnnxSeq2SeqConfigWithPast(OnnxConfig):
        pass

    def compute_effective_axis_dimension(*args, **kwargs):
        raise NotImplementedError("transformers.onnx unavailable (transformers v5)")""",
)

add_patch(
    "tokenization_indictrans.py",
    """        # Store token content directly instead of accessing .content
        self.unk_token = (
            hasattr(unk_token, "content") and unk_token.content or unk_token
        )
        self.pad_token = (
            hasattr(pad_token, "content") and pad_token.content or pad_token
        )
        self.eos_token = (
            hasattr(eos_token, "content") and eos_token.content or eos_token
        )
        self.bos_token = (
            hasattr(bos_token, "content") and bos_token.content or bos_token
        )""",
    """        # Unwrap AddedToken -> str BEFORE super() (transformers v5 forbids
        # assigning special tokens before super().__init__() has run)
        unk_token = getattr(unk_token, "content", unk_token)
        pad_token = getattr(pad_token, "content", pad_token)
        eos_token = getattr(eos_token, "content", eos_token)
        bos_token = getattr(bos_token, "content", bos_token)""",
)

add_patch(
    "tokenization_indictrans.py",
    """        # Validate tokens
        if self.unk_token not in self.src_encoder:
            raise KeyError("<unk> token must be in vocab")
        if self.pad_token not in self.src_encoder:
            raise KeyError("<pad> token must be in vocab")""",
    """        # Validate tokens
        if unk_token not in self.src_encoder:
            raise KeyError("<unk> token must be in vocab")
        if pad_token not in self.src_encoder:
            raise KeyError("<pad> token must be in vocab")""",
)

add_patch(
    "tokenization_indictrans.py",
    """        # Initialize current settings
        self._switch_to_input_mode()

        # Cache token IDs
        self.unk_token_id = self.src_encoder[self.unk_token]
        self.pad_token_id = self.src_encoder[self.pad_token]
        self.eos_token_id = self.src_encoder[self.eos_token]
        self.bos_token_id = self.src_encoder[self.bos_token]

        super().__init__(
            src_vocab_file=self.src_vocab_fp,
            tgt_vocab_file=self.tgt_vocab_fp,
            do_lower_case=do_lower_case,
            unk_token=unk_token,
            bos_token=bos_token,
            eos_token=eos_token,
            pad_token=pad_token,
            **kwargs,
        )""",
    """        super().__init__(
            src_vocab_file=self.src_vocab_fp,
            tgt_vocab_file=self.tgt_vocab_fp,
            do_lower_case=do_lower_case,
            unk_token=unk_token,
            bos_token=bos_token,
            eos_token=eos_token,
            pad_token=pad_token,
            **kwargs,
        )

        # Initialize current settings (v5: only after special-token state exists)
        self._switch_to_input_mode()

        # Cache token IDs
        self.unk_token_id = self.src_encoder[self.unk_token]
        self.pad_token_id = self.src_encoder[self.pad_token]
        self.eos_token_id = self.src_encoder[self.eos_token]
        self.bos_token_id = self.src_encoder[self.bos_token]""",
)

# --- modeling_indictrans.py: variant-aware (two different export vintages) ---

# newer export (en-indic): tie_weights already has my kwarg comment but calls
# the v4-only _tie_or_clone_weights helper.
add_patch(
    "modeling_indictrans.py",
    """    def tie_weights(self, *args, **kwargs):
        # transformers v5 calls tie_weights(recompute_mapping=...); args are
        # ignored here so tying behaves exactly as it did under transformers 4.x
        if self.config.share_decoder_input_output_embed:
            self._tie_or_clone_weights(self.model.decoder.embed_tokens, self.lm_head)""",
    """    def tie_weights(self, *args, **kwargs):
        # transformers v5 compat: _tie_or_clone_weights was removed; share the
        # Parameter directly (same dst<-src direction as the v4 helper)
        if self.config.share_decoder_input_output_embed:
            self.model.decoder.embed_tokens.weight = self.lm_head.weight""",
    required=False,
)

# older export (indic-en): plain no-arg tie_weights stub.
add_patch(
    "modeling_indictrans.py",
    """    def tie_weights(self):
        pass""",
    """    def tie_weights(self, *args, **kwargs):
        # transformers v5 calls tie_weights(recompute_mapping=...); tying for
        # this export happens in __init__ (lm_head.weight = embed_tokens.weight)
        pass""",
    required=False,
)

# older export only: inherit GenerationMixin explicitly (v5 dropped it from
# PreTrainedModel; the newer export already has this line).
add_patch(
    "modeling_indictrans.py",
    "from transformers.modeling_utils import PreTrainedModel",
    "from transformers.modeling_utils import PreTrainedModel\n"
    "from transformers.generation.utils import GenerationMixin",
    required=False,
)
add_patch(
    "modeling_indictrans.py",
    "class IndicTransForConditionalGeneration(IndicTransPreTrainedModel):",
    "class IndicTransForConditionalGeneration(IndicTransPreTrainedModel, GenerationMixin):",
    required=False,
)


# Older config vintage lacks config.json's vocab_size key, but transformers v5
# beam search reads config.vocab_size (the output vocabulary).
add_patch(
    "configuration_indictrans.py",
    "        self.decoder_vocab_size = decoder_vocab_size",
    """        self.decoder_vocab_size = decoder_vocab_size
        # transformers v5 generation reads config.vocab_size (= output vocab)
        self.vocab_size = getattr(self, "vocab_size", decoder_vocab_size)""",
    required=False,
)

# Older export only: its forward replaced the standard labels handling with a
# prepare_decoder_input_ids_label() helper meant for teacher-forcing evaluation
# (it trims the last decoder token and requires a non-None decoder_attention_mask).
# Both break autoregressive generation, so the upstream contract is restored.
_TEACH_FORCING_CALL = (
    "        decoder_input_ids, decoder_attention_mask, labels = "
    "prepare_decoder_input_ids_label(decoder_input_ids,\n"
    + " " * len(
        "        decoder_input_ids, decoder_attention_mask, labels = "
        "prepare_decoder_input_ids_label("
    )
    + "decoder_attention_mask)"
)
add_patch(
    "modeling_indictrans.py",
    _TEACH_FORCING_CALL,
    """        # transformers v5 bridge: restore the upstream generation contract.
        # The mirror's prepare_decoder_input_ids_label() helper is for
        # teacher-forcing evaluation (trims the last decoder token, requires a
        # non-None decoder_attention_mask) and breaks autoregressive generation.
        if labels is not None:
            if decoder_input_ids is None:
                decoder_input_ids = shift_tokens_right(
                    labels, self.config.pad_token_id, self.config.decoder_start_token_id
                )""",
    required=False,
)

# --- modeling_indictrans.py: transformers v5 KV-cache bridge (both copies) ---
# v5 generation passes/returns Cache objects (tuples are rejected) while these
# v4-era models consume and produce legacy tuples
# (self_k, self_v, cross_k, cross_v) per decoder layer.

add_patch(
    "modeling_indictrans.py",
    "        outputs = self.model(",
    """        # transformers v5 bridge: Cache -> legacy tuple (this v4-era model
        # consumes tuples; a fresh/empty cache becomes None = no past)
        if past_key_values is not None and not isinstance(past_key_values, (tuple, list)):
            past_key_values = self._cache_to_legacy_past(past_key_values)

        outputs = self.model(""",
    required=False,
)

add_patch(
    "modeling_indictrans.py",
    """        return Seq2SeqLMOutput(
            loss=masked_lm_loss,
            logits=lm_logits,
            past_key_values=outputs.past_key_values,""",
    """        # transformers v5 bridge: legacy tuple -> Cache so beam search
        # (reorder) and the next decoding step receive a Cache object
        if isinstance(outputs.past_key_values, (tuple, list)):
            outputs.past_key_values = self._legacy_past_to_cache(outputs.past_key_values)

        return Seq2SeqLMOutput(
            loss=masked_lm_loss,
            logits=lm_logits,
            past_key_values=outputs.past_key_values,""",
    required=False,
)

_REORDER_NEW = """    @staticmethod
    def _reorder_cache(past_key_values, beam_idx):
        # transformers v5 bridge: Cache objects reorder themselves; the legacy
        # tuple path below is kept for non-generation use
        if hasattr(past_key_values, "reorder_cache"):
            past_key_values.reorder_cache(beam_idx)
            return past_key_values
        reordered_past = ()
        for layer_past in past_key_values:
            reordered_past += (
                tuple(
                    past_state.index_select(0, beam_idx) for past_state in layer_past
                ),
            )
        return reordered_past"""

# newer export formatting (black-linted)
add_patch(
    "modeling_indictrans.py",
    """    @staticmethod
    def _reorder_cache(past_key_values, beam_idx):
        reordered_past = ()
        for layer_past in past_key_values:
            reordered_past += (
                tuple(
                    past_state.index_select(0, beam_idx) for past_state in layer_past
                ),
            )
        return reordered_past""",
    _REORDER_NEW,
    required=False,
)

# older export formatting (single-line tuple)
add_patch(
    "modeling_indictrans.py",
    """    @staticmethod
    def _reorder_cache(past_key_values, beam_idx):
        reordered_past = ()
        for layer_past in past_key_values:
            reordered_past += (tuple(past_state.index_select(0, beam_idx) for past_state in layer_past),)
        return reordered_past""",
    _REORDER_NEW,
    required=False,
)

add_patch(
    "modeling_indictrans.py",
    "    def prepare_inputs_for_generation(",
    '''    def _cache_to_legacy_past(self, cache):
        # transformers v5 bridge: EncoderDecoderCache -> legacy tuple of
        # (self_k, self_v, cross_k, cross_v) per decoder layer
        from transformers.cache_utils import EncoderDecoderCache

        if not isinstance(cache, EncoderDecoderCache):
            return cache
        sc, cc = cache.self_attention_cache, cache.cross_attention_cache
        legacy = []
        for i in range(len(self.model.decoder.layers)):
            sl = sc.layers[i] if i < len(sc.layers) and sc.layers[i].is_initialized else None
            cl = cc.layers[i] if i < len(cc.layers) and cc.layers[i].is_initialized else None
            legacy.append(
                (
                    sl.keys if sl is not None else None,
                    sl.values if sl is not None else None,
                    cl.keys if cl is not None else None,
                    cl.values if cl is not None else None,
                )
            )
        if all(x is None for layer in legacy for x in layer):
            return None
        return tuple(legacy)

    def _legacy_past_to_cache(self, legacy):
        # transformers v5 bridge: legacy tuple -> EncoderDecoderCache
        from transformers.cache_utils import DynamicCache, EncoderDecoderCache

        sc, cc = DynamicCache(), DynamicCache()
        for i, layer in enumerate(legacy):
            if layer is None:
                continue
            sk, sv = layer[0], layer[1]
            ck, cv = (layer[2], layer[3]) if len(layer) >= 4 else (None, None)
            if sk is not None:
                sc.update(sk, sv, i)
            if ck is not None:
                cc.update(ck, cv, i)
        return EncoderDecoderCache(sc, cc)

    def prepare_inputs_for_generation(''',
    required=False,
)


def patch_file(path: pathlib.Path) -> None:
    src = io.open(path, encoding="utf-8").read()
    changed = False
    for old, new, required in PATCHES.get(path.name, []):
        if new in src:
            print(f"  already applied : {path.name} | {old.splitlines()[0][:60]!r}")
            continue
        if old not in src:
            if required:
                raise SystemExit(f"UNEXPECTED content, refusing to patch: {path}")
            print(f"  variant absent  : {path.name} | {old.splitlines()[0][:60]!r}")
            continue
        src = src.replace(old, new, 1)
        changed = True
    if changed:
        io.open(path, "w", encoding="utf-8", newline="\n").write(src)
        compile(src, str(path), "exec")  # syntax check only
        print(f"  patched         : {path}")


if __name__ == "__main__":
    root = pathlib.Path(__file__).resolve().parents[1]
    for model in (
        "models/indictrans2-en-indic-dist-200M",
        "models/indictrans2-indic-en-dist-200M",
    ):
        model_dir = root / model
        if not model_dir.exists():
            print(f"missing (skipped): {model_dir}")
            continue
        for fname in PATCHES:
            f = model_dir / fname
            if f.exists():
                patch_file(f)
            else:
                print(f"missing (skipped): {f}")
